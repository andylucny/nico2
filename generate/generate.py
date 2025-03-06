import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import sys

class DK(nn.Module):

    def __init__(self, device='cpu'):
        super(DK, self).__init__()
        self.device = device
        self.t90 = torch.tensor(90.0).to(self.device)
        self.t180 = torch.tensor(180.0).to(self.device)
        self.point0 = torch.tensor([[0., 0., 0., 1.0]], dtype=torch.float32, requires_grad=False).T.to(self.device)
        self.vector0 = torch.tensor([[0., 0., 1.0]], dtype=torch.float32, requires_grad=False).T.to(self.device)
        self.e = torch.eye(4, dtype=torch.float32, requires_grad=False).to(self.device)
        
    def rad(self, value):
        return value * torch.pi / 180.0

    def Txyz(self, B, tx, ty, tz):
        tr = torch.eye(4).to(self.device)
        tr[0,3] = tx
        tr[1,3] = ty
        tr[2,3] = tz
        return tr.unsqueeze(0).repeat(B,1,1)

    def Rz(self, thetas):
        B = thetas.shape[0]
        thetas = self.rad(thetas)
        tr = torch.eye(4).to(self.device)
        tr = tr.unsqueeze(0).repeat(B,1,1)
        tr[:,0,0] = torch.cos(thetas)
        tr[:,0,1] = -torch.sin(thetas)
        tr[:,1,0] = torch.sin(thetas)
        tr[:,1,1] = torch.cos(thetas)
        return tr

    def Rx(self, alphas):
        B = alphas.shape[0]
        alphas = self.rad(alphas)
        tr = torch.eye(4).to(self.device)
        tr = tr.unsqueeze(0).repeat(B,1,1)
        tr[:,1,1] = torch.cos(alphas)
        tr[:,1,2] = -torch.sin(alphas)
        tr[:,2,1] = torch.sin(alphas)
        tr[:,2,2] = torch.cos(alphas)
        return tr

    def Ry(self, betas):
        B = betas.shape[0]
        betas = self.rad(betas)
        tr = torch.eye(4).to(self.device)
        tr = tr.unsqueeze(0).repeat(B,1,1)
        tr[:,0,0] = torch.cos(betas)
        tr[:,0,2] = torch.sin(betas)
        tr[:,2,0] = -torch.sin(betas)
        tr[:,2,2] = torch.cos(betas)
        return tr

    def Ts(self, thetas):
        B = thetas.shape[0]
        t90 = self.t90.unsqueeze(0).repeat(B)
        t180 = self.t180.unsqueeze(0).repeat(B)
        return [
            self.Txyz(B,0,5,19.5), self.Rz(t90), self.Rz(thetas[:,0]), # -> 'r_shoulder_z'
            self.Txyz(B,0,-1.5,2.5), self.Ry(t90), self.Rz(thetas[:,1]), # -> 'r_shoulder_y'
            self.Txyz(B,3,0,9.5), self.Rx(-t90), self.Rz(-thetas[:,2]), # -> 'r_arm_x'
            self.Txyz(B,17.5,0,0), self.Rx(t90), self.Rz(t180), self.Rz(-thetas[:,3]), # -> 'r_elbow_y'
            self.Txyz(B,10,0,0), self.Ry(t90), self.Rz(-thetas[:,4]/2.0), # -> 'r_wrist_z'
            self.Txyz(B,0,0,10), self.Rx(-t90), self.Rz(-t90), self.Rz(thetas[:,5]/4.5+10), # -> 'r_wrist_x'
            self.Txyz(B,0,-1,0), self.Txyz(B,6,0,0), self.Rz(20+(thetas[:,6]+180)/4.5), self.Txyz(B,6,0,0), self.Ry(t90) # -> 'r_indexfinger_x'
        ]

    def dk(self, thetas):
        B = thetas.shape[0]
    
        Ts = self.Ts(thetas)
        re = self.e.unsqueeze(0).repeat(B, 1, 1)
        for T in Ts:  
            re = torch.bmm(re, T) 
            
        point0 = self.point0.unsqueeze(0).repeat(B, 1, 1)
        points = torch.bmm(re, point0).squeeze(-1)[:, :3]  

        vector0 = self.vector0.unsqueeze(0).repeat(B, 1, 1)
        vectors = torch.bmm(re[:, :3, :3], vector0).squeeze(-1) 
            
        return points, vectors

    def forward(self, x):
        return self.dk(x)

class IK(nn.Module):

    def __init__(self, N, device='cpu'):
        super(IK, self).__init__()
        self.device = device
        self.layer = nn.Linear(N+1,7,bias=False)
        self.angles_from = torch.tensor([-30.0,-30.0,0.0,50.0,-180.0,-180.0,-180.0],dtype=torch.float32).to(device)
        self.angles_to = torch.tensor([80.0,180.0,70.0,180.0,180.0,180.0,180.0],dtype=torch.float32).to(device)
        self.dk = DK(device=device)

    def forward(self, x): # (N+1) x 1 [0-1] -> (N+1) x 7 [logit] -> (N+1) x 7 [dg] -> (N+1) x 3 [cm]
        logits = (self.layer.weight * inputs).t()
        poses = self.angles_from.unsqueeze(0) + torch.sigmoid(logits)*(self.angles_to-self.angles_from).unsqueeze(0)
        points, vectors = self.dk(poses) # calculation
        return points, vectors, poses

device = 'cuda'

# Example usage
if __name__ == "__main__":
    # Instantiate the model
    N = 50
    model = IK(N,device=device).to(device)

    # Example input
    ind = int(sys.argv[1]) if len(sys.argv[1]) > 1 else 1
    touch_postures = { # new
        1 : [33.0, 39.0, 25.0, 134.0, 102.0, 77.0, -168.0],
        2 : [37.0, 31.0, 23.0, 119.0, 107.0, 113.0, -177.0],
        3 : [57.0, 33.0, 40.0, 134.0, 80.0, 36.0, -159.0],
        4 : [51.0, 54.0, 37.0, 161.0, 92.0, 38.0, -174.0],
        5 : [38.0, 49.0, 36.0, 154.0, 80.0, 61.0, -177.0],
        6 : [25.0, 38.0, 31.0, 133.0, 99.0, 86.0, -156.0],
        7 : [34.0, 17.0, 39.0, 107.0, 106.0, 78.0, -180.0],
    }
    start_pose = [-24.92, 81.45, 46.55, 94.37, -59.03, 28.0, 45.67]
    touch_pose = touch_postures[ind]
    ends = torch.tensor([start_pose, touch_pose]).to(device)
    
    # Forward pass
    output_points, output_vectors = model.dk(ends)
    start_point, touch_point = output_points
    
    goal_vector = touch_point - start_point
    normalized_goal_vector = (goal_vector / goal_vector.norm()).to(device)
    
    fractions = (torch.arange(N+1,dtype=torch.float32).to(device))/N
    goal_points = start_point + fractions.unsqueeze(1) * goal_vector
    inputs = torch.ones(1,N+1).float().to(device)    
    optimizer = torch.optim.Adam(model.parameters(), lr=0.1)

    def save(poses):
        dofs = ['r_shoulder_z', 'r_shoulder_y', 'r_arm_x', 'r_elbow_y', 'r_wrist_z', 'r_wrist_x', 'r_indexfinger_x']
        with open(f'generated{ind}.txt','wt') as f:
            f.write(str(dofs)+'\n')
            for pose in poses:
                f.write(str([angle.item() for angle in pose])+'\n')
        print('saved')    

    # Training loop
    total_epoches = 0
    best_loss = 1e9
    def train(num_epochs = 500):
        global total_epoches, best_loss
        for epoch in range(num_epochs):
            total_loss = 0.0
            optimizer.zero_grad()  # Clear gradients
            points, vectors, poses = model(inputs)  # Forward pass
            loss1 = ((points - goal_points)**2).mean()
            loss2 = (1.0-(vectors @ normalized_goal_vector.unsqueeze(0).t())).mean()
            loss3 = ((poses[0] - ends[0])**2).sum()
            loss4 = ((poses[-1] - ends[1])**2).sum()
            loss5 = ((points[0] - start_point)**2).sum()
            loss6 = ((points[-1] - touch_point)**2).sum()
            loss7 = (torch.diff(poses,dim=0)**2).mean()
            loss = loss1 + 50*loss2 + 5*loss3 + 100*loss4 + 10*loss5 + 200*loss6 + loss7
            loss.backward()  # Backpropagation
            optimizer.step()  # Update weights
            total_loss += loss.item()

            print(f"Epoch [{epoch+total_epoches+1}/{total_epoches+num_epochs}], Loss: {total_loss:.4f}")
            if total_loss < best_loss:
                best_loss = total_loss
                if best_loss < 10.0:
                    save(poses)

        total_epoches += num_epochs

    train(3000)
    print("Training completed, best loss:", best_loss)
   
    def test():
        postures = []
        with open(f'generated{ind}.txt','r') as f:
            lines = f.readlines()
            dofs = eval(lines[0])
            for line in lines[1:]:
                posture = eval(line)
                postures.append(posture)
        
        poses = torch.tensor(postures).float().to(device)
        points, vectors = model.dk(poses)
        print('start pose')
        print(start_pose)    
        print(poses[0])
        print("====================================")
        print('touch pose')
        print(touch_pose)    
        print(poses[-1])
        print("====================================")
        print('start point')
        print(start_point)    
        print(points[0])
        print("====================================")
        print('touch point')
        print(touch_point)    
        print(points[-1])
        print("====================================")
        print((vectors @ normalized_goal_vector.unsqueeze(0).t()).squeeze(-1))
        print((points-goal_points).norm(dim=1))
    