from flegmgui import Window


app = Window("Flegm Build Console", width=620, height=900)
app.label("Flegm Build Console")
app.label("Prepare, validate, and ship a release from one focused workspace")
app.separator()
overall_status = app.label("Pipeline ready")
app.label("Overall progress")


def update_overall(value: int) -> None:
    if value >= 100:
        overall_status.set("Pipeline complete - release is ready")
    elif value > 0:
        overall_status.set(f"Pipeline running - {value}% complete")
    else:
        overall_status.set("Pipeline ready")


overall_progress = app.progress(0, update_overall)
app.separator()
app.label("Pipeline stages")
compile_status = app.label("Waiting to compile")
compile_progress = app.progress(0)
test_status = app.label("Waiting to test")
test_progress = app.progress(0)
package_status = app.label("Waiting to package")
package_progress = app.progress(0)
app.separator()
app.label("Release options")


def update_compile(value: int) -> None:
    compile_status.set("Compilation complete" if value >= 100 else f"Compiling source - {value}%")


def update_tests(value: int) -> None:
    test_status.set("Tests passed" if value >= 100 else f"Running tests - {value}%")


def update_package(value: int) -> None:
    package_status.set("Package created" if value >= 100 else f"Packaging release - {value}%")


compile_progress.set_on_change(update_compile)
test_progress.set_on_change(update_tests)
package_progress.set_on_change(update_package)
def run_pipeline() -> None:
    compile_progress.animate_to(100, speed=6)
    if run_tests.checked:
        test_progress.animate_to(100, speed=4)
    else:
        test_progress.set(0)
        test_status.set("Tests skipped")
    if create_package.checked:
        package_progress.animate_to(100, speed=3)
    else:
        package_progress.set(0)
        package_status.set("Packaging skipped")
    overall_progress.animate_to(100, speed=2)


def reset_pipeline() -> None:
    overall_progress.set(0)
    compile_progress.set(0)
    test_progress.set(0)
    package_progress.set(0)
    run_tests.set(False)
    create_package.set(False)
    compile_status.set("Waiting to compile")
    test_status.set("Waiting to test")
    package_status.set("Waiting to package")
    overall_status.set("Pipeline ready")


def show_summary() -> None:
    completed = sum(progress.value >= 100 for progress in (compile_progress, test_progress, package_progress))
    overall_status.set(f"Release summary: {completed}/3 stages complete")


options = app.row(gap=18, padding=10, background=0x00FFFFFF)
run_tests = options.checkbox("Run the test suite")
create_package = options.checkbox("Create a distributable package")

actions = app.row(gap=12, padding=10, background=0x00FFFFFF)
actions.button(
    "Run pipeline",
    run_pipeline,
    background=0x00395DD9,
    hover_background=0x004B70E8,
    pressed_background=0x002D49A7,
)
actions.button(
    "Show summary",
    show_summary,
    background=0x005A7DCE,
    hover_background=0x006B8EE0,
    pressed_background=0x00476AB5,
)
actions.button(
    "Reset pipeline",
    reset_pipeline,
    background=0x006B7785,
    hover_background=0x007C8998,
    pressed_background=0x00535E6B,
)
app.run()
