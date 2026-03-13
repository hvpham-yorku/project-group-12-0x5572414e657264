import os
import subprocess
import sys

testsToRun = [
    "test.path_constructor.test_path_constructor",
    "test.logic.test_videoEditing_VideoCropper",
    "test.logic.test_videoEditing_FirstFrameExtractor",
    "test.logic.test_videoEditing_merge_and_blend_images",
    "test.logic.test_videoEditing_merge_and_blend_videos",
    "test.logic.test_singleton",
    "test.test_logic.test_customerAttributesEstimator",
    "test.pages.test_logWindow",
    "test.pages.test_addStorePopup",
    "test.pages.test_addStorePopup_ui",
    "test.pages.test_menuBar_cleanup",
    "test.pages.test_cameraZoneWindow_videos",
    "test.pages.test_cameraMergeWindow_ui",
    "test.pages.test_cameraZoneWindow_ui",
    "test.integration.test_gui_workflows",
]


def main():
    for test in testsToRun:
        print(f"\n\n\nTESTING THE {test} CLASS OF TESTS!!!!!!")
        subprocess.run(
            [
                sys.executable,
                "-m",
                test,
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
