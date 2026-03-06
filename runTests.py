import os
import subprocess

testsToRun = [
    "test.logic.test_videoEditing_VideoCropper",
    "test.logic.test_videoEditing_FirstFrameExtractor",
]


def main():
    for test in testsToRun:
        print(f"\n\n\nTESTING THE {test} CLASS OF TESTS!!!!!!")
        subprocess.run(
            [
                "python",
                "-m",
                test,
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
