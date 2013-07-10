import shutil
from string import Template

SPEC_IN = 'repo.spec.in'
SPEC_FMT = '%s.spec'

def generate_spec(tmpl, channel):
    data = {
        'channel': channel
    }
    tmpl = Template(tmpl)

    spec = open(SPEC_FMT % channel, "w")
    spec.write(tmpl.substitute(data))
    spec.close()

if __name__ == '__main__':
    channels = ['stable', 'unstable', 'master']
    spec_tmpl = open(SPEC_IN).read()
    for channel in channels:
        generate_spec(spec_tmpl, channel)
