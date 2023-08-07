import whisper
import os

sizes = ["tiny", "small","base",  "medium"]

for size in sizes:
    model = whisper.load_model(size, device="cpu")

    # get all files in samples directory
    files = os.listdir("samples")

    # loop through all files
    for i, file in enumerate(files):    
        # load audio (full system path) and pad/trim it to fit 30 seconds
        path = os.path.join(os.path.dirname(__file__), "samples", file)
        print(path)

        audio = whisper.load_audio(path)
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # detect the spoken language
        _, probs = model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")

        # decode the audio
        options = whisper.DecodingOptions(language="ur")
        result = whisper.decode(model, mel, options,fp16 = False)

        # print the recognized text
        print(result.text)

        # make sure the results directory exists else create it
        if not os.path.exists("results"):
            os.makedirs("results")

        if not os.path.exists("results/" + size):
            os.makedirs("results/" + size)

        # save the recognized text to a file
        with open(f"results/{size}/{i}.txt", "w", encoding="utf-8") as f:
            f.write(result.text)
