# Tech Stack: Calibration Optimization

## Core Libraries
- **Python 3.x**
- **MyPTV**: `myptv.extendedZolof.camera`, `myptv.extendedZolof.calibrate`
- **NumPy**: For array manipulation and coordinate grouping.
- **Pandas**: (Optional) For easy I/O if needed, though `loadtxt` from NumPy is preferred for consistency with the existing codebase.

## Development Tools
- **Conductor**: For tracking progress and managing the implementation track.
- **Git**: For version control.
- **Pytest**: For verifying the optimization algorithm against mock point data.

## Execution Environment
- **Platform**: macOS (Darwin) as per current session.
- **Environment**: Virtual environment `venv/` with `myptv` installed in editable mode.
