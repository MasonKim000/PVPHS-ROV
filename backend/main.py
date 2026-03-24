import cv2


def main():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cv2.imwrite("test.jpg", frame)
    cap.release()


if __name__ == "__main__":
    main()
