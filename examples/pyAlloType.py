# a python Wrapper for AlloType
import re
import os
import click


CMD_Template = f"""_F_

_P_

1
_cutoff_

_PA_

1
_cutoff_
_PS_

1
_cutoff_
pocketA
gen-pocket 4.5
gen-force
test
back
pocketAS
gen-pocket 4.5
gen-force
test
back
energy
exit
"""
EXE_AlloType = './AlloType'


def check_existence(folder, stem):
    full_path = os.path.join(folder, '%s.pdb' % stem)
    assert full_path


@click.command()
@click.option('-f', '--folder', required=True, help='folder for pdb files')
@click.option('-p', '--protein', required=True, help='pdb filename for P/Protein/apo, without .pdb')
@click.option('-a', '--allo', required=True, help='pdb filename for PA/Protein+allosteric ligand, without .pdb')
@click.option('-s', '--substrate', required=True, help='pdb filename for PS/Protein+substrate ligand, without .pdb')
@click.option('--cutoff', default=9, type=float, required=True, help='cutoff distances between residues, default 9å')
def main(folder, protein, allo, substrate, cutoff):
    for stem in [protein, allo, substrate]:
        check_existence(folder, stem)

    cmd = CMD_Template
    cmd = cmd.replace('_F_', folder)
    cmd = cmd.replace('_P_', protein)
    cmd = cmd.replace('_PA_', allo)
    cmd = cmd.replace('_PS_', substrate)
    cmd = cmd.replace('_cutoff_', str(cutoff))
    with open('input.cmd', 'w') as fp:
        fp.write(cmd)

    cmd = f'{EXE_AlloType} < input.cmd > allotype.output'
    print(cmd)
    os.system(cmd)

    numbers = []
    with open('allotype.output', 'r') as fp:
        rex = re.compile(r'([-\.0-9]+)\sKcal\/mol')
        lines = fp.readlines()[-14:]
        for line in lines:
            mo = rex.findall(line)
            if mo:
                numbers.append(float(mo[0]))
        # print(numbers)
        assert len(numbers) == 13
    
    result = {
        'PS_dG': numbers[0],
        'PA_dG': numbers[3],
        'PAS_dG': numbers[6],
        'ddG': numbers[9]
    }
    print(result)
    print(f"Allosteric type = {'POSITIVE' if result['ddG'] < 0 else 'NEGATIVE'}, based on ddG value.")


if __name__ == '__main__':
    main()