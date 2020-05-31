from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
import typing
import os

from gtts import gTTS
from pydub import AudioSegment


@dataclass
class Exercise:
    """Class for holding the details of an exercise segment"""
    name: str
    duration: int  # seconds
    reps: typing.Optional[int] = None
    language: str = "en"
    slow: bool = False

    def instruction_text(self) -> str:
        if self.reps:
            text = f"{self.reps} {self.name} in {self.duration} seconds"
        else:
            text = f"{self.name} for {self.duration} seconds"
        return text

    def create_speech_obj(self) -> gTTS:
        speech_obj = gTTS(text=self.instruction_text(), lang=self.language, slow=self.slow)
        return speech_obj


class Mp3Creator:
    """Joins Exercise objects along with beeps and silence intervals into a single file"""

    Segment = namedtuple('Segment', ['exercise', 'speech_obj', 'audio_file_path'])

    def __init__(self, exercises: list):
        self.segments = self._create_segments(exercises)
        p = Path(".") / "audio_resources"
        self.beep_start = AudioSegment.from_mp3(f"{p.absolute()}/beep_start.mp3")
        self.beep_end = AudioSegment.from_mp3(f"{p.absolute()}/beep_end.mp3")
        self.finished_sound = AudioSegment.from_mp3(f"{p.absolute()}/workout_end.mp3")
        self.pause = AudioSegment.silent(2500)  # milliseconds

    def _create_segments(self, exercises: list):
        segments = []
        for i, exercise in enumerate(exercises):
            speech_obj = exercise.create_speech_obj()
            filename = f"audio{i}.mp3"
            segment = self.Segment(exercise, speech_obj, filename)
            segments.append(segment)
        return segments

    def create_mp3(self):
        self._create_segment_files()

        final_mp3 = AudioSegment.silent(2000)
        for segment in self.segments:
            final_mp3 += AudioSegment.from_mp3(segment.audio_file_path)

        final_mp3 += self.finished_sound

        p = Path(".") / "output" / "new.mp3"
        new_file_name = p.absolute()
        final_mp3.export(new_file_name, format="mp3")

        self._delete_segment_files()

        return new_file_name

    def _create_segment_files(self):
        for segment in self.segments:
            segment.speech_obj.save(segment.audio_file_path)
            self._add_beeps_and_silence_to_segment_file(segment)

    def _add_beeps_and_silence_to_segment_file(self, segment: Segment):
        speech = AudioSegment.from_mp3(segment.audio_file_path)
        MILLISECONDS = 1000
        silence = AudioSegment.silent(segment.exercise.duration * MILLISECONDS)
        new_audio = speech + self.pause + self.beep_start + silence + self.beep_end

        new_audio.export(segment.audio_file_path, format="mp3")

    def _delete_segment_files(self):
        for segment in self.segments:
            os.remove(segment.audio_file_path)


if __name__ == '__main__':

    def load_exercises_from_workbook(filepath):
        from openpyxl import load_workbook

        wb = load_workbook(filepath)
        ws = wb.active
        exercises = []
        for i, row in enumerate(ws.iter_rows()):
            if i == 0:
                continue
            if row[2].value:
                exercise = Exercise(row[0].value, int(row[1].value), int(row[2].value))
            else:
                exercise = Exercise(row[0].value, int(row[1].value))
            exercises.append(exercise)
        return exercises


    p = Path.home() / 'Documents' / 'Leg Stretch Workout.xlsx'
    exercises = load_exercises_from_workbook(p.absolute())

    creator = Mp3Creator(exercises)
    creator.create_mp3()
