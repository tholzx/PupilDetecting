import sys
import cv2 as cv
import numpy as np
import os

#np.seterr(over='ignore')

# проблемы с переполнением (были)
def is_pupil_center(a,b):
    global c1, c2, c3, c4
    if ((c1 + a > c1 * 2 + 12) or (c1 + a < c1 * 2 - 12)):
        if ((c3 + a > c3 * 2 + 10) or (c3 + a < c3 * 2 - 10)):
            return False
        else:
            return True
    elif ((c2 + b > c2 * 2 + 12) or (c2 + b < c2 * 2 - 12)):
        if ((c4 + b > c4 * 2 + 10) or (c4 + b < c4 * 2 - 10)):
            return False
        else:
            return True
    else:
        return True



def find_pupil(argv, direct, filename):

    ##  [load]
    default_file = str(direct) + '/' + str(filename)
    filename = argv[0] if len(argv) > 0 else default_file

    # Read image
    src = cv.imread(filename, cv.IMREAD_COLOR)

    # If image is loaded not fine
    if src is None:
        print ('Error opening image!')
        print ('Usage: hough_circle.py [image_name -- default ' + default_file + '] \n')
        return -1
    ## [load]

    ## [convert]
    lab = cv.cvtColor(src, cv.COLOR_BGR2LAB)

    # -----Splitting the LAB image to different channels-------------------------
    l, a, b = cv.split(lab)

    # -----Applying CLAHE to L-channel-------------------------------------------
    clahe = cv.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
    cl = clahe.apply(b)

    # -----Merge the CLAHE enhanced L-channel with the a and b channel-----------
    limg = cv.merge((l,a,cl))
    #limg = cv.merge((cl, a, b))

    # -----Converting image from LAB Color model to RGB model--------------------
    src = cv.cvtColor(limg, cv.COLOR_LAB2BGR)

    gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    ## [convert]

    ## [reduce_noise]
    # Reduce the noise to avoid false circle detection
    gray = cv.medianBlur(gray, 15)
#    cv.imshow('gray', gray)
    ## [reduce_noise]

    #ret, th1 = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    th2 = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, \
                               cv.THRESH_BINARY, 11, 3)

    # Otsu's thresholding
    th3 = cv.threshold(gray,127,255,cv.THRESH_TRUNC)
    # Otsu's thresholding after Gaussian filtering
    blur = cv.GaussianBlur(gray, (5, 5), 0)
    ret3, th4 = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

#    cv.imshow('th2', th2)
    #     cv.imshow('th3', th3)
#    cv.imshow('th4', th4)
#    cv.waitKey()

####### it works
#    cv.imshow('th2', th2)
   # gray = th2
    ## [houghcircles]
    rows = gray.shape[0]
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, rows / 8,
                               param1=50, param2=25, #50,25
                               minRadius=20, maxRadius=50) #80, 110 (15,50)
    ## [houghcircles]

    ## [draw]
    global c1, c2, c3, c4, accuracy
    if circles is not None:
        #print filename
        print('\n', default_file, " | ", end='')
        circles = np.uint16(np.around(circles))
        circles.setflags(write=True)
        for i in circles[0, :]:
            center = (i[0], i[1])

            pupil = is_pupil_center(i[0], i[1])
            # print true or false center is detected
            print(center, " | ", pupil, " || ", end='')

            # circle center
            cv.circle(src, center, 1, (0, 255, 0), 3)
            # circle outline
            radius = i[2]
            cv.circle(src, center, radius, (0, 255, 0), 1)
            # print (center)



            # if pupil center is true put new coordinates of center
            if (pupil == True):
                c1 = i[0]
                c2 = i[1]
                c3 = c1
                c4 = c2
                accuracy += 1
            else:
                #if not, put new fake coordinates of center
                c3 = i[0]
                c4 = i[1]


    else:

        print('\n', default_file, " |e ", end='')
        circles = cv.HoughCircles(th2, cv.HOUGH_GRADIENT, 1, 20,
                                  param1=20, param2=24, # 50,25
                                  minRadius=20, maxRadius=60)  # 80, 110 (15,50)
        circles = np.uint16(np.around(circles))
        circles.setflags(write=True)
        for i in circles[0, :]:
            center = (i[0], i[1])

            pupil = is_pupil_center(i[0], i[1])
            # print true or false center is detected
            print(center, " | ", pupil, " || ", end='')

            # circle center
            cv.circle(src, center, 1, (0, 255, 0), 3)
            # circle outline
            radius = i[2]
            cv.circle(src, center, radius, (127, 255, 0), 3)
            # print (center)

            # if pupil center is true put new coordinates of center
            if (pupil == True):
                c1 = i[0]
                c2 = i[1]
                c3 = c1
                c4 = c2
            else:
                # if not, put new fake coordinates of center
                c3 = i[0]
                c4 = i[1]
    ## [draw]

    ## [display]
#    cv.imshow(default_file, src)
#    cv.waitKey(0)
#    cv.destroyAllWindows()
    ## [display]

    return



def main():

    global c1,c2,c3,c4, accuracy
    #первая фотография не определяется отдельной функцией, так что будет false
    # real center
    c1 = 698
    c2 = 420
    # imagine center
    c3 = c1
    c4 = c2

    accuracy = 0;
    number_of_files = 0

    #-----------------ВВЕСТИ ПРЯМОЙ ПУТЬ К КАТAЛОГУ --------------------------
    direct = "d:/Python/Eye/img/yellow"
    for root, dirs, files in os.walk(direct):
        for file in files:
            if file.endswith(".png") or file.endswith(".jpeg") or file.endswith(".jpg"):
                find_pupil(sys.argv[1:], direct, file)
                number_of_files += 1
                #print(os.path.join(root, file))

    print ("\n\n%d / %d is defined.\n accuracy = %.2f" % (accuracy, number_of_files, (accuracy*100/number_of_files)))


if __name__ == '__main__':
    main()
