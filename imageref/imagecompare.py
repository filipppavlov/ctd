import subprocess
import os

NVIMGDIFF_EXE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'bin', 'nvimgdiff'))

SIZE_DIFFER_MESSAGE = '--- NOTE: only the overlap between the 2 images'
MESSAGES = {'mean_abs_error': '  Mean absolute error: ', 'max_abs_error': '  Max absolute error: ',
            'root_mean_squared_error': '  Root mean squared error: ',
            'peak_signal_to_noise': '  Peak signal to noise ratio in dB: '}
SECTION_NAMES = {'color': 'Color:', 'alpha': 'Alpha:'}


class DimensionsDiffer(RuntimeError):
    pass


def compare_images(path1, path2):
    lines = subprocess.check_output([NVIMGDIFF_EXE, '-alpha', path1, path2]).split('\n')
    result = {'color': {}, 'alpha': {}}
    section = None
    for line in lines:
        if line.startswith(SIZE_DIFFER_MESSAGE):
            raise DimensionsDiffer()
        for each in SECTION_NAMES:
            if line.startswith(SECTION_NAMES[each]):
                section = each
                break
        for each in MESSAGES:
            if line.startswith(MESSAGES[each]):
                result[section][each] = float(line[len(MESSAGES[each]):])
    return result