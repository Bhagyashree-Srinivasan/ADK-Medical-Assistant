
VALIDATION_PROMPT = '''You are a transcription validator.

You will be given:
1. An {audio_file}, and
2. A {transcript} of that audio.

Your task is to **review the transcript against the audio** and identify any transcription errors.
You have to follow the audio exactly, do **not** summarize, interpret, or rephrase — just follow the spoken words exactly.

If you find a mistake, output the following for each error:
- **Line number** where the mistake occurs (based on the transcript input)
- **The incorrect text, the whole line with the incorrect text**
- **The corrected text** based on what was actually said in the audio, the whole line

If there are no mistakes, return: `No transcription errors found.`

At the end output are the mistakes found medically impactful, or just smaller errors (slight rephrasing, or missed random words, or stop words and similar).

**Format your output like this:**
Line 7
Incorrect: Patient: I started talking the medicine yesterday.
Correct:   Patient: I started taking the medicine yesterday.
.
.
.

Medically impactful: YES (lines: 7)


Transcript:
'''