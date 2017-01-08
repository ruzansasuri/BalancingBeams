import re
import turtle as t

class Beam:
    __slots__ = ('left', 'right','scale')

    def __init__(self,l = [], r = []):
        self.left = l
        self.right = r
        self.scale = 0


class Weight:
    __slots__ = ('distance', 'value')

    def __init__(self, d, v):
        self.distance = d
        self.value = v

    def __str__(self):
        return str(self.distance)


def file_check(file, perm = 'r'):
    try:
        f = open(file, perm)
        return f
    except FileNotFoundError:
        print("File", file, "does not exist...")
        exit()


def create_beam(file):
    beam_dict = dict()
    count = 0
    for beams in file:
        if beams[0] != 'B':
            print('File is incorrect. Each line should start with B.')
            exit()
        i = 1
        num = 0
        if bool(re.search(r'\d', beams[i])):
            while bool(re.search(r'\d', beams[i])):
                num = num * 10 + int(beams[i])
                i += 1
        elif beams[i] != ' ':
            print('File is incorrect. B should be followed by a positive integer or a space in case of the root.')
        beam_list = []
        dist = 'x'
        val = 0
        neg = 0
        b = 0
        for j in beams[i+1:]:
            if j == '-':
                neg = 1
            elif j == 'B':
                b = 1
            elif bool(re.search(r'\d', j)):
                val = val * 10 + int(j)
            elif j == ' ' or j == "\n":
                if neg == 1:
                    val = 0 - val
                elif b == 1:
                    val = 'B'+str(val)
                if dist == 'x':
                    dist = val
                else:
                    beam_list.append((dist, val))
                    dist = 'x'
                val = 0
                neg = 0
                b = 0
            if j == "\n":
                break
        beam_dict[num] = beam_list
        count += 1
    if not(j == '\n'):
        print("Last line must be blank.")
        exit()
    return count, beam_dict


def create_tree(count, beam_dict):
    beam_list = []
    for i in range(count):
        left = []
        right = []
        for w in beam_dict[i]:
            if bool(re.search(r'\d', str(w[1]))):
                if w[0] < 0:
                    d = 0 - w[0]
                    we = Weight(d, w[1])
                    left.append(we)
                else:
                    we = Weight(w[0], w[1])
                    right.append(we)
            else:
                if w[0] < 0:
                    d = 0 - w[0]
                    we = Weight(d, w[1][1:])
                    left.append(we)
                else:
                    we = Weight(w[0], w[1][1:])
                    right.append(we)
        left = sorted(left, key=lambda weight: weight.distance)
        right = sorted(right, key=lambda weight: weight.distance)
        b = Beam(left,right)
        beam_list.append(b)
    change_list_to_tree(beam_list, 0)
    return beam_list[0]


def change_list_to_tree(beam_list, i):
        beams = beam_list[i]
        for l in beams.left:
            if bool(re.search(r'B', str(l.value))):
                li = int(l.value[1:])
                change_list_to_tree(beam_list, li)
                l.value = beam_list[li]
        for r in beams.right:
            if bool(re.search(r'B', str(r.value))):
                ri = int(r.value[1:])
                change_list_to_tree(beam_list, ri)
                r.value = beam_list[ri]

def find_miss(beam_root):
    v = 0
    left_or_right = 'left'
    lsum = 0
    rsum = 0
    tweight = 0
    for item in beam_root.left:
        if item.value == -1:
            v = 1
        elif type(item.value) is Beam:
            x = find_miss(item.value)
            if x is None:
                return None
            else:
                lsum += x * item.distance
        else:
            lsum += item.value * item.distance
            tweight += item.value
    for item in beam_root.right:
        if item.value == -1:
            v = 1
            left_or_right = 'right'
        elif type(item.value) is Beam:
            x = find_miss(item.value)
            if x is None:
                return None
            else:
                rsum += x * item.distance
        else:
            rsum += item.value * item.distance
            tweight += item.value
    if v == 0:
        return tweight
    else:
        if left_or_right == 'left':
            for item in beam_root.left:
                if item.value == -1:
                    torque = rsum - lsum
                    item.value = torque // item.distance
        else:
            for item in beam_root.right:
                if item.value == -1:
                    torque = lsum - rsum
                    item.value = torque // item.distance
        return None


def find_scale(beam_root, pixel_diff, mult_factor):
    l = beam_root.left[len(beam_root.left) - 1]
    r = beam_root.right[len(beam_root.right) - 1]
    dl = (0,0)
    dr = (0,0)
    s = 0
    if type(beam_root.left[0].value) is Beam:
        dl = find_scale(beam_root.left[0].value, pixel_diff, mult_factor)
    if type(beam_root.right[0].value) is Beam:
        dr = find_scale(beam_root.right[0].value, pixel_diff, mult_factor)
    last_one = [dl[0],dr[1]]
    d = beam_root.left[0].distance + beam_root.right[0].distance
    max = (dl[1] + dr[0] + pixel_diff/mult_factor) // d
    first = True
    pitem = beam_root.left[0]
    for item in beam_root.left:
        if first:
            first = False
            continue
        d = 0
        if type(item.value) is Beam:
            d = find_scale(item.value, pixel_diff, mult_factor)
            if item == l:
                last_one[0] = d
        s = (dl[0] + d + pixel_diff/mult_factor) // (item.distance - pitem.distance)
        if s > max:
            max = s
        dl = (d, d)
        pitem = item
    pitem = beam_root.right[0]
    first = True
    for item in beam_root.right:
        if first:
            first = False
            continue
        d = 0
        if type(item.value) is Beam:
            d = find_scale(item.value,pixel_diff, mult_factor)
            if item == r:
                last_one[1] = d
        s = (dr[1] + d + pixel_diff/mult_factor) // (item.distance - pitem.distance)
        if s > max:
            max = s
        dr = (d,d)
        pitem = item
    dl = max * l.distance + last_one[0]
    dr = max * r.distance + last_one[1]
    beam_root.scale = max * mult_factor
    return dl, dr

def draw(beam, line):
    t.down()
    t.forward(line)
    t.right(90)
    d = 0
    pitem = Weight(0,0)
    for item in beam.left:
        t.down()
        t.forward(beam.scale * (item.distance - pitem.distance))
        t.left(90)
        if type(item.value) is Beam:
            draw(item.value,line)
        else:
            t.forward(line)
            t.up()
            t.forward(line*4/3)
            t.write(item.value)
            t.back(line*4/3)
            t.back(line)
        t.right(90)
        d += beam.scale * (item.distance - pitem.distance)
        pitem = item

    t.back(d)
    t.right(180)
    pitem = Weight(0,0)
    d = 0

    for item in beam.right:
        t.down()
        t.forward(beam.scale * (item.distance - pitem.distance))
        t.right(90)
        if type(item.value) is Beam:
            draw(item.value, line)
        else:
            t.forward(line)
            t.up()
            t.forward(line*4/3)
            t.down
            t.write(item.value)
            t.back(line*4/3)
            t.back(line)
        t.left(90)
        d += beam.scale * (item.distance - pitem.distance)
        pitem = item

    t.back(d)
    t.right(90)
    t.back(line)

def draw_helper(beam_root, line):
    t.setup(800, 800)
    t.up()
    t.left(90)
    t.forward(400)
    t.right(180)
    draw(beam_root, line)

def main():
    #beam file should have one extra blank line at the bottom
    PIXEL_DIFF = 40
    LINE_SIZE = 20
    MULTIPLICATION_FACTOR = 10
    input_file = input("Please enter the name of the file: ")
   #input_file = 'beams.txt'
    infile = file_check(input_file)
    beams = create_beam(infile)
    beam_root = create_tree(beams[0],beams[1])
    find_miss(beam_root)
    find_scale(beam_root,PIXEL_DIFF, MULTIPLICATION_FACTOR)
    draw_helper(beam_root,LINE_SIZE)
    t.mainloop()

if __name__ == '__main__':
    main()
