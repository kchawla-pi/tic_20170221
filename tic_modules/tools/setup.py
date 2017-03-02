from distutils.core import setup

setup(
    name = 'tic_tools',
    version = '1.0',
    description = 'tic_tools module with custom tic functions',
    author = 'Kshtij Chawla',
    author_email = 'kc.insight.pi@gmail.com',
    url = 'https://github.com/kchawla-pi',
    py_modules = [
        'bipolar',
        'extract_b0',
        '_qa_utilities',
        'sort_nii',
        'ants_ct',
        'cummean_nii',
        'extract_volumes',
        'json_utils',
        'reorder',
        '_utilities',
        'ants_lct',
        'cumsum_nii',
        'grow_labels',
        'plot_overlay',
        'setup',
        'wmlesions'
    ]
)