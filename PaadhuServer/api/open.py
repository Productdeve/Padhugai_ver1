import cv2


def FrameCapture(path):
    # Path to video file
    vidObj = cv2.VideoCapture(path)

    # Used as counter variable
    count = 0

    # checks whether frames were extracted
    success = 1

    while success:
        # vidObj object calls read
        # function extract frames
        success, image = vidObj.read()

        # Saves the frames with frame-count
        cv2.imwrite("C:/Users/MYPC/Downloads/images/frame%d.jpg" % count, image)

        count += 1


# Driver Code
if __name__ == '__main__':
    # Calling the function
    FrameCapture("C:/Users/MYPC/Downloads/C8701.mp4")