#!/bin/bash
scp *.py dev@pi.local:/home/dev/laboratory/electronics
scp static/* dev@pi.local:/home/dev/laboratory/electronics/static
scp templates/* dev@pi.local:/home/dev/laboratory/electronics/templates
