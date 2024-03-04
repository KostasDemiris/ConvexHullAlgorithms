#!/usr/bin/env python
# coding: utf-8

# In[1]:


# By Kostas Demiris
import math
import random

def get_smallest_point(point_set):
    # Returns the right-most bottom point
    minimum = [-float('inf'), float('inf')]
    for point in point_set:
        if point[1] < minimum[1] or (point[1] == minimum and point[0] > minimum[0]):
            minimum = point
    return minimum

def create_random_set_of_points(max_points, max_x, max_y):
    return list(set([(random.randint(0,max_x),random.randint(0,max_y)) for i in range(max_points)]))

def is_concave(a, b, c):
    return ((b[0] - a[0]) * (c[1] - a[1])) - ((b[1] - a[1]) * (c[0] - a[0])) > 0 

def cross_product(a, b, c):
    return ((b[0] - a[0]) * (c[1] - a[1])) - ((b[1] - a[1]) * (c[0] - a[0]))

def angle_to_positive(source, destination):
    # Finds the polar angle of the line between source to destination
    delta_x = destination[0] - source[0]
    delta_y = destination[1] - source[1]
    angle = math.atan2(delta_y, delta_x)
    if angle < 0:
        angle = 2 * math.pi + angle
    if delta_x == 0 and delta_y < 0:
        return (1.5) * math.pi
    if delta_y == 0 and delta_x < 0:
        return 2 * math.pi
    
    return angle

def prev(index, array):
    # Returns the previous point in a circular array
    return array[index-1]

def next_(index, array):
    # Returns the next point in a circular array
    return array[(index+1)%len(array)]

def graham_scan(point_set):
    # https://lvngd.com/blog/convex-hull-graham-scan-algorithm-python/ was where i learnt this from
    initial_point = get_smallest_point(point_set)
    out_stack = []
    sorted_points = sorted(point_set, key=lambda point, initial_point = initial_point: angle_to_positive(initial_point, point))
    for point in sorted_points:
        while len(out_stack) >= 3 and not is_concave(out_stack[-2], out_stack[-1], point):
            # This way it also removes colinear points
            out_stack.pop(-1)
        out_stack.append(point)
        
    if len(out_stack) >= 3 and not is_concave(out_stack[0], out_stack[1], out_stack[2]):
        out_stack.pop(1)
    if len(out_stack) >= 3 and not is_concave(out_stack[-2], out_stack[-1], out_stack[0]):
        out_stack.pop(-1)
        
    return out_stack


# In[2]:


# utility functions for chan's algorithm

def create_sub_hulls(point_set, k):
    # Just seperates the point set into k sized subset, and returns the convex hulls of those subsets
    sub_hulls = []
    i = 0
    while (k * (i+1) < len(point_set)):
        sub_hulls.append(graham_scan(point_set[(k*i): (k * (i+1))]))
        i+=1
    remainder = graham_scan(point_set[(k*i): min(k * (i+1), len(point_set)+1)])
    if len(remainder) > 0:
        sub_hulls.append(remainder)
    return sub_hulls

def is_right_tangent(external_point, mid_point, prev_point, next_point):
    # If these conditions are satisfied, we've found the right tangent
    return is_concave(external_point, mid_point, prev_point) and is_concave(external_point, mid_point, next_point)

def right_most_tangent(source, poly):
    # https://gist.github.com/tixxit/252229 was the inspiration for this approach
    lower = 0; upper = len(poly)-1
    mid = (upper + lower)//2
    
    if len(poly) <= 2:
        # These are just the manual cases that we can get out of the way immediately by literally comparing them
        if len(poly) == 1:
            return poly[0]
        else:
            if cross_product(source, poly[0], poly[1]) > 0:
                return poly[0]
            elif cross_product(source, poly[0], poly[1]) == 0:
                return max([poly[0], poly[1]], key=lambda point, origin = source: distance(origin, point))
            else:
                return poly[1]
    
    left_prev = cross_product(source, poly[0], prev(0, poly)) >= 0
    left_next = cross_product(source, poly[0], next_(0, poly)) >= 0 
        
    while lower < upper:
        mid = (upper + lower) // 2
        previous = is_concave(source, poly[mid], prev(mid, poly))
        _next = is_concave(source, poly[mid], next_(mid, poly))
        # Is concave basically checks if it "bends inwards" so to speak, which we check with cross product

        
        if poly[mid] == source:
            # Just by definition
            return next_(mid, poly)
        
        if previous and _next:
            return poly[mid]    
        # While it is not the case that both points lie to the "left" of the line
    
        left_leaning = is_concave(source, poly[lower], poly[mid])
        # Depending on where the mid value lies, it means that when you move to the next point in the hull
        # it moves either left or right relative to the line between source and poly[mid]
        
        if is_right_tangent(source, poly[mid], prev(mid, poly), next_(mid, poly)):
            if poly[mid] == source:
                # just by definition
                return next_(mid, poly)
            else:
                return poly[mid]
        
        if (left_leaning and ((not left_next) or left_prev) or (not left_leaning and not previous)):
            upper = mid
        else:
            lower = mid + 1 # This avoids the issue with odd numbers of points in sub_hull causing issues with the 
            # the whole integer division method.
            
            left_prev = is_concave(source, poly[lower], prev(lower, poly))
            left_next = is_concave(source, poly[lower], next_(lower, poly))  
            
    if poly[lower] == source:
        return next_(lower, poly)
    return poly[lower] 

def distance(a, b):
    return (((b[0] - a[0]) ** 2) + ((b[1] - a[1]) ** 2))
    
def find_smallest_tangent(source, sub_hulls):
    # this takes the tangent from the source to each subhull, and returns the smallest one
    current_best = right_most_tangent(source, sub_hulls[0])
    tangent_record = [current_best]
    for sub_hull in sub_hulls[1:]:
        tangent_point = right_most_tangent(source, sub_hull)
        tangent_record.append(tangent_point)
        if cross_product(source, current_best, tangent_point) < 0:
            # if it's concave, then the point lies anti-clockwise from the current best so it's not the next convex hull point
            current_best = tangent_point
        elif cross_product(source, current_best, tangent_point) == 0 and distance(source, current_best) < distance(source, tangent_point):
            # We don't want colinear points
            current_best = tangent_point
    return current_best


# In[3]:


# Chan's algorithm
def chansAlgorithm(points):
    inLoop = False
    n = len(points) - 1 
    k = 3 # The size of the subsets we start of with. Ideal k is equal to h, the number of hull points.
    first_point = get_smallest_point(points)
    
    while True:
        sub_hulls = create_sub_hulls(points, k)
        hull_points = [first_point]
        next_point = None
        iterations_passed = 0       
        in_hull = dict()
        
        while iterations_passed < (len(points) + 1):
            # the biggest convex hull possible has all points on it, so one with more points in the hull than the
            # input set is impossible
            tangent_point = find_smallest_tangent(hull_points[-1], sub_hulls)
            if tangent_point == first_point:
                # By definition, all convex hull points have been discovered so we can return the discovered ones
                return hull_points
            
            else:
                hull_points.append(tangent_point)
                if in_hull.get(tangent_point) != None:
                    iterations_passed = 2 * len(points)
                    # This drastically speeds up things for skipping smaller k steps, and checking retrieval is o(1)
                    in_hull[tangent_point] = "In"
                
            iterations_passed += 1

        if k ** 2 > len(points) - 1:
            if inLoop:
                return False
            # We don't want it to infinitely loop in a program where it can't find the convex hull.
            inLoop = True
        k = min(k ** 2, len(points)) # Quickly grows to be at, or greater than, h. As suggested in his paper.


# In[4]:


# Matplotlib visualisations and some test cases
import matplotlib.pyplot as plt
import timeit

def seperate_x_y(array_2d):
    x, y = [], []
    for point in array_2d:
        x.append(point[0])
        y.append(point[1])
    return (x, y)

def generate_circle(points_on_hull, total_points):
    # This allows you to test with varying numbers of points on the rim
    points = []
    for i in range(points_on_hull):
        points.append((math.floor(30267 * (math.cos(i * (2 * math.pi) / points_on_hull) + 1)), math.floor(30267 * (math.sin(i * (2 * math.pi) / points_on_hull) + 1))))
    generated = 0
    while generated < total_points - points_on_hull:
        generated_point = (random.randint(0, 30267), random.randint(0, 30267))
        if distance((15133, 15133), generated_point) < 229007689:
            # this is 15133 squared, basically if its inside the circle 
            points.append(generated_point)
            generated += 1
    return points

def verify_by_comparision(point_set):
    if graham_scan(point_set) == chansAlgorithm(point_set):
        return True
    return False

def display_graham(point_s):
    xss, yss = seperate_x_y(point_s)
    graham_x, graham_y = seperate_x_y(graham_scan(point_s))
    graham_x.append(graham_x[0]); graham_y.append(graham_y[0])
    
    plt.plot(xss, yss, 'o')
    plt.plot(graham_x, graham_y)
    plt.show()
    print(f"graham's is \n{graham_scan(point_s)}")
    
def display_chans(point_s):
    xss, yss = seperate_x_y(point_s)
    chan_x, chan_y = seperate_x_y(chansAlgorithm(point_s))
    chan_x.append(chan_x[0]); chan_y.append(chan_y[0])
    
    plt.plot(xss, yss, 'o')
    plt.plot(chan_x, chan_y)
    plt.show()
    print(f"chan's is \n{chansAlgorithm(point_s)}")
    
def validate_by_comparision(point_s):
    return (graham_scan(point_s) == chansAlgorithm(point_s))

def get_breaking_points(size):
    tests = 0
    print("Started breaking")
    the_test_point_set = create_random_set_of_points(size, 30276, 30276)
    
    while validate_by_comparision(the_test_point_set):
        print(f"the number of tests has been {tests}")
        tests += 1
        the_test_point_set = create_random_set_of_points(size, 30276, 30276)
        if tests >= 100:
            print(f"Passed 100 tests for sets of size {size}, considered to have passed")
            return
    display_graham(the_test_point_set)
    display_chans(the_test_point_set)
    print("\n\n\nchans", chansAlgorithm(the_test_point_set), "\n", "Graham's", graham_scan(the_test_point_set))
    print("\n\n", the_test_point_set)
    
def time_test():
    i = 10
    sizes = []
    time_graham = []
    time_chan = []
    print("This is for the average time in a set of 5 completely random point sets")
    while i <= 10000:
        points_timeit = create_random_set_of_points(i, 32767, 32767)
        sizes.append(i)
        time_chan.append(timeit.timeit(lambda: chansAlgorithm(points_timeit), number=10))
        time_graham.append(timeit.timeit(lambda: graham_scan(points_timeit), number=10))
        print(f"The time taken in chan for size {i} is {time_chan[-1]/10}")
        print(f"The time taken in graham for size {i} is {time_graham[-1]/10}")
        print(f"\nthe tests returned {validate_by_comparision(points_timeit)}\n")
        i *= 2
    plt.plot(sizes, time_chan, 'r*')
    for pair in zip(sizes, time_chan):
        plt.annotate('(%.5f, %.5f)' % pair, xy=pair)
    plt.show()
    
    i = 10
    sizes = []
    time_graham = []
    time_chan = []
    print("This is for the average time in a set of 5 high_hull point sets")
    while i <= 10000:
        points_timeit = generate_circle(math.floor(i/5), i)
        # This is an insanely high number of points on the hull, so 1/5th of all points are on the hull.
        # Also try an amount in between this, such as i * (0.5) since the "random" drawing from a disk
        # is usually i * (1/3), so would possible be a better "high" hull test.
        sizes.append(i)
        time_chan.append(timeit.timeit(lambda: chansAlgorithm(points_timeit), number=10))
        time_graham.append(timeit.timeit(lambda: graham_scan(points_timeit), number=10))
        print(f"The time taken in chan for size {i} is {time_chan[-1]/10}")
        print(f"The time taken in graham for size {i} is {time_graham[-1]/10}")
        print(f"\nthe tests returned {validate_by_comparision(points_timeit)}\n")
        i *= 2
        
    i = 10
    sizes = []
    time_graham = []
    time_chan = []
    print("This is for the average time in a set of 5 low_hull point sets")
    while i <= 10000:
        points_timeit = generate_circle(math.floor(math.log(i) + 4), i)
        sizes.append(i)
        time_chan.append(timeit.timeit(lambda: chansAlgorithm(points_timeit), number=10))
        time_graham.append(timeit.timeit(lambda: graham_scan(points_timeit), number=10))
        print(f"The time taken in chan for size {i} is {time_chan[-1]/10}")
        print(f"The time taken in graham for size {i} is {time_graham[-1]/10}")
        print(f"\nthe tests returned {validate_by_comparision(points_timeit)}\n")
        i *= 2
    
get_breaking_points(10000)
# display_chans(create_random_set_of_points(100, 3000, 3000))
# time_test()


# In[ ]:





# In[ ]:





# In[ ]:



