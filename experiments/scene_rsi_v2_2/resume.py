"""Continue scheduled missing work, or only redraw when all tasks are terminal."""
from pathlib import Path
import argparse
import subprocess
import sys
import pilot

ROOT=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--recover-incident',type=int,choices=[1,2,3])
    args=parser.parse_args()
    if (ROOT/'service_pause.json').exists():
        if args.recover_incident is None:raise SystemExit('Service pause retained. After connectivity recovery, use the next unused bounded incident check; no marker is silently removed.')
        subprocess.run([sys.executable,str(ROOT/'recovery_check.py'),'--incident',str(args.recover_incident)],check=True,env=pilot.cpu_environment())
    elif args.recover_incident is not None:raise SystemExit('No service pause exists; no unnecessary recovery model call submitted')
    final=pilot.read(ROOT/'FINAL_STATUS.json')
    if final and final['all_scheduled_terminal']:
        import analyze
        analyze.main();print('All scheduled work already terminal; redraw only, no new CLI or Blender calls');return
    import experiment
    experiment.experiment_a()
    if not (ROOT/'tests/MECHANISM_ACCEPTANCE.json').exists():
        subprocess.run([sys.executable,str(ROOT/'mechanism_tests.py')],check=True,env=pilot.cpu_environment())
    if not (ROOT/'configs/BC_freeze.json').exists():
        subprocess.run([sys.executable,str(ROOT/'freeze_bc.py')],check=True,env=pilot.cpu_environment())
    import diagnosis_runner
    diagnosis_runner.main()
    import analyze
    analyze.main()
    summary=pilot.read(ROOT/'metrics/C_summary.json')
    terminal=all(summary[m]['terminal']==summary[m]['scheduled'] for m in ['v2_1_fixed','v2_2_evidence'])
    pilot.write_json(ROOT/'FINAL_STATUS.json',{'all_scheduled_terminal':terminal,'A_scheduled':24,
        'C_scheduled_arm_tasks':20,'ledger':pilot.current(),'new_automatic_M_descendants':0})


if __name__=='__main__':main()
