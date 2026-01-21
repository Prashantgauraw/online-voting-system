from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(str1):
    speak = Dispatch(("SAPI.SpVoice"))
    speak.Speak(str1)

def check_if_exists(value):
    try:
        with open("votes.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0] == value:
                    return True
    except FileNotFoundError:
        print("File not found or unable to open the CSV file.")
    return False

def write_vote(output, party, date, timestamp, exist):
    filename = "votes.csv"
    mode = "a" if exist else "w"
    with open(filename, mode, newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not exist:
            writer.writerow(['NAME', 'VOTE', 'DATE', 'TIME'])
        writer.writerow([output[0], party, date, timestamp])

def main():
    video = cv2.VideoCapture(0)
    if not video.isOpened():
        print("Error: Could not open video device.")
        return

    facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    if not os.path.exists('data/'):
        os.makedirs('data/')

    # Check if the file exists and is not empty
    file_path = 'data/names.pkl'
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"Error: The file {file_path} does not exist or is empty.")
        return

    try:
        with open(file_path, 'rb') as f:
            LABELS = pickle.load(f)
    except EOFError:
        print(f"Error: The file {file_path} is empty or corrupted.")
        return
    except Exception as e:
        print(f"An error occurred while loading the file {file_path}: {e}")
        return

    # Similarly, check and load FACES
    file_path = 'data/faces_data.pkl'
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"Error: The file {file_path} does not exist or is empty.")
        return

    try:
        with open(file_path, 'rb') as f:
            FACES = pickle.load(f)
    except EOFError:
        print(f"Error: The file {file_path} is empty or corrupted.")
        return
    except Exception as e:
        print(f"An error occurred while loading the file {file_path}: {e}")
        return

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(FACES, LABELS)

    imgBackground = cv2.imread("imgBackground.jpg")
    output = None

    try:
        while True:
            ret, frame = video.read()
            if not ret:
                print("Error: Could not read frame from video device.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = facedetect.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                crop_img = frame[y:y + h, x:x + w]
                try:
                    resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
                    output = knn.predict(resized_img)

                    ts = time.time()
                    date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
                    timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                    exist = os.path.isfile("votes.csv")

                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)
                    cv2.rectangle(frame, (x, y - 40), (x + w, y), (0, 0, 255), -1)
                    cv2.putText(frame, str(output[0]), (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                except Exception as e:
                    print(f"Error processing face: {e}")
                    continue

            try:
                # Resize the frame to match the region in the background image
                frame = cv2.resize(frame, (450, 300))
                imgBackground[250:250 + 300, 170:170 + 450] = frame
            except Exception as e:
                print(f"Error overlaying frame: {e}")
                continue

            cv2.imshow('frame', imgBackground)
            k = cv2.waitKey(1)

            if output is not None:
                voter_exist = check_if_exists(output[0])
                if voter_exist:
                    speak("you have already voted")
                    break

                if k == ord('1'):
                    speak("you have successfully voted to BJP")
                    time.sleep(3)
                    write_vote(output, "BJP", date, timestamp, exist)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTION")
                    break
                elif k == ord('2'):
                    speak("you have successfully voted to SP")
                    time.sleep(3)
                    write_vote(output, "SP", date, timestamp, exist)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTION")
                    break
                elif k == ord('3'):
                    speak("you have successfully voted to CONGRESS")
                    time.sleep(3)
                    write_vote(output, "CONGRESS", date, timestamp, exist)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTION")
                    break
                elif k == ord('4'):
                    speak("you have successfully voted to AAP")
                    time.sleep(3)
                    write_vote(output, "APP", date, timestamp, exist)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTION")
                    break
                elif k == ord('5'):
                    speak("you have successfully voted to BSP")
                    time.sleep(3)
                    write_vote(output, "BSP", date, timestamp, exist)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTION")
                    break
                elif k == ord('6'):
                    speak("you have successfully voted to NOTA")
                    time.sleep(3)
                    write_vote(output, "NOTA", date, timestamp, exist)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTION")
                    break

            if k == 27:  # ESC key to exit
                break
    finally:
        video.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()