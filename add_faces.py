import os
import cv2
import pickle
import numpy as np
import sys  # Needed for a clean exit

# Create data folder if it doesn't exist
if not os.path.exists('data/'):
    os.makedirs('data/')
# Aadhaar input and validation
name = input("Enter your valide Aadhaar number: ")

if len(name) != 12 or not name.isdigit():
    print("Aadhaar number does not exist")
    sys.exit()  # Exit the script

# Delete existing pickle files (optional)
if os.path.exists('data/faces_data.pkl'):
    os.remove('data/faces_data.pkl')
if os.path.exists('data/names.pkl'):
    os.remove('data/names.pkl')

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
faces_data = []
i = 0
framesTotal = 51
captureAfterFrame = 2

while True:
    ret, frame = video.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w]
        resized_img = cv2.resize(crop_img, (50, 50))
        if len(faces_data) < framesTotal and i % captureAfterFrame == 0:
            faces_data.append(resized_img)
        i += 1
        cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)

    cv2.imshow('frame', frame)
    k = cv2.waitKey(1)
    if k == ord('q') or len(faces_data) >= framesTotal:
        break

video.release()
cv2.destroyAllWindows()

# Ensure we have exactly framesTotal samples
if len(faces_data) > framesTotal:
    faces_data = faces_data[:framesTotal]
elif len(faces_data) < framesTotal:
    print(f"Warning: Only captured {len(faces_data)} frames instead of {framesTotal}")
    framesTotal = len(faces_data)

# Convert list of images to numpy array and reshape
faces_data = np.array(faces_data)
faces_data = faces_data.reshape((len(faces_data), -1))

# Create or update names.pkl
names = [name] * len(faces_data)
file_path = 'data/names.pkl'
if not os.path.exists(file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(names, f)
else:
    with open(file_path, 'rb') as f:
        existing_names = pickle.load(f)
    names = existing_names + names
    with open(file_path, 'wb') as f:
        pickle.dump(names, f)

# Create or update faces_data.pkl
file_path = 'data/faces_data.pkl'
if not os.path.exists(file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(faces_data, f)
else:
    with open(file_path, 'rb') as f:
        existing_faces = pickle.load(f)
    faces_data = np.vstack((existing_faces, faces_data))
    with open(file_path, 'wb') as f:
        pickle.dump(faces_data, f)

print(f"Saved {len(faces_data)} face samples and {len(names)} labels")
