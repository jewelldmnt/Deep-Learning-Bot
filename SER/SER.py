import numpy as np
import librosa.display
import joblib
import pyaudio
import wave
import soundfile

# load the pre-trained model for emotion recognition
model = joblib.load('emotion_recognition_model.h5')

# function to record live audio
def record_audio(filename):
    duration = 5  # in seconds
    sample_rate = 44100
    channels = 1
    # Set up the PyAudio object
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)

    # Start recording
    print("Imik na anteh...")
    frames = []
    for i in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    print("Oh shh awat na, ingay.")

    # Stop the stream and close the PyAudio object
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Write the recorded audio data to a WAV file
    wave_file = wave.open(filename, "wb")
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wave_file.setframerate(sample_rate)
    wave_file.writeframes(b"".join(frames))
    wave_file.close()

# function to extract 180 features
def extract_feature(filename, mfcc, chroma, mel):
    with soundfile.SoundFile(filename) as sound_file:
        X = sound_file.read(dtype="float32")
        sample_rate = sound_file.samplerate
        if chroma:
            stft = np.abs(librosa.stft(X))
        result = np.array([])
        if mfcc:
            mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
            result = np.hstack((result, mfccs))
        if chroma:
            chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)
            result = np.hstack((result, chroma))
        if mel:
            mel = np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate).T, axis=0)
            result = np.hstack((result, mel))
    return result

# Predict the emotion of the audio file
def predict_emotion(filename):
    features = extract_feature(filename, mfcc=True, chroma=True, mel=True)
    prediction = model.predict([features])[0]
    return prediction


if __name__ == "__main__":
    # live audio is saved in output.wav
    file_name = "output.wav"
    record_audio(file_name)

    # Use the predict_emotion function on an audio file
    predicted_emotion = predict_emotion(file_name)
    print("The predicted emotion is:", predicted_emotion)