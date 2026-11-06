from common import ROOT,read,call,write
folder=ROOT/'smoke_cli_sol'
if not (folder/'session.json').exists():
    answer,session=call('Describe the visible furniture and its colors in this actual attached image in one short sentence. This is an attachment connectivity test, not a reconstruction proposal.',read(ROOT/'config.json')['model'],folder,[ROOT/'tasks/smoke01/reference.png'],role='sol_image_connectivity')
    write(folder/'attachment_check.json',{'response':answer,'requested_model':session['requested_model'],'returned_model':session['actual_model'],'image_passed_by_CLI_attachment':True})
