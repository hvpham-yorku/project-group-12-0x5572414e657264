import subprocess
import sys

unitTests = [
    "test.unit.src.test_path_constructor",
    "test.unit.src.logic.test_videoEditing_VideoCropper",
    "test.unit.src.logic.test_videoEditing_FirstFrameExtractor",
    "test.unit.src.logic.test_videoEditing_merge_and_blend_images",
    "test.unit.src.logic.test_videoEditing_merge_and_blend_videos",
    "test.unit.src.logic.test_singleton",
    "test.unit.src.logic.test_customerAttributesEstimator",
    "test.unit.src.pages.test_logWindow",
    "test.unit.src.pages.test_addStorePopup",
    "test.unit.src.pages.test_menuBar_cleanup",
    "test.unit.src.pages.test_cameraZoneWindow_videos",
]

customerTests = [
    "test.customer.src.pages.test_addStorePopup_ui",
    "test.customer.src.pages.test_cameraMergeWindow_ui",
    "test.customer.src.pages.test_cameraZoneWindow_ui",
]

integrationTests = [
    "test.integration.src.pages.test_gui_workflows",
]

testsToRun = unitTests + customerTests + integrationTests


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
