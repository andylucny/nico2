from ellipse import generate_perimeter as generate_perimeter_of_ellipse

def shape_of_P(sz):
    # letter P
    shape = []
    for z in range(sz):
        shape.append([0,sz-z])
    for z in range(sz,0,-5):
        shape.append([0,sz-z])
    for x, y in generate_perimeter_of_ellipse(sz/4,sz/2,sz):
        shape.append([-x,y+sz-sz/4])
    return shape

if __name__ == "__main__":

    import matplotlib.pyplot as plt
    import time
    
    sz = 30
    points = shape_of_P(sz)
    
    y_vals, z_vals = zip(*points)
    #plt.plot(y_vals, z_vals, 'o-')
    #plt.gca().set_aspect('equal')
    #plt.show()
    
    def generate_colors_red_to_blue(N):
        return [(1 - i / (N - 1), 0, i / (N - 1)) for i in range(N)]
    
    def plot_points_gradually(x_vals, y_vals, delay_ms=100):
        plt.figure()
        plt.xlim(-20, 5)
        plt.ylim(-5, 35)
        plt.axis('equal')
        plt.grid(True)

        colors = generate_colors_red_to_blue(len(x_vals))
        for i in range(len(x_vals)):
            plt.plot(x_vals[i], y_vals[i], 'o', color=colors[i])
            plt.pause(delay_ms / 1000.0)

        plt.show()

    plot_points_gradually(y_vals, z_vals)
