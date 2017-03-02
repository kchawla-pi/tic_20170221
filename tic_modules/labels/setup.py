from setuptools import setup

setup(
    name = 'tic_labels',
    version = '170228.0-dev',
    description = 'tic_labels module with custom tic functions',
    author = 'Kshtij Chawla',
    author_email = 'kc.insight.pi@gmail.com',
    url = 'https://github.com/kchawla-pi',
    py_mocules = [
        'calculate_phase_ghosts',
        'create_mask',
        'ellipsoid',
        'keep',
        'measure',
        'remove',
        'where',
        'cat_csv',
        'create_pial_mask',
        'extract',
        'label_connected_components',
        'merge',
        'set',
        'common',
        'create_qa_labels',
        'list',
        'overlap',
        'setup',
        'create_cube',
        'create_sphere',
        'join',
        'measure_phase_ghosts',
        'properties',
        'sort']
)


