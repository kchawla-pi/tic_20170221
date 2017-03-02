import configparser


def get_api_key(inifile, projectname):
    """
    Returns the API key for a Redcap project.

    :param inifile: file containing the API keys for Redcap projects
    :param projectname: name of project as specified in inifile
    :return: api_key (string)

    """

    apitoken = '000'

    config = configparser.ConfigParser()
    flist = config.read(inifile)

    if len(flist) == 0:
        print('Cannot read INI file {a}'.format(a=inifile))
    else:
        pnames = config.options('APIKey')
        for pnam in pnames:
            if pnam.lower() == projectname.lower():
                apitoken = config.get('APIKey', pnam)
                break

    return apitoken
