from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from django.http import JsonResponse
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import subprocess, time


genomeName = ""
doCheck = True

def getSiteSSH(siteName):
    
    cmd = ''
    if siteName == "Fabric":
        print(siteName+' selected')
        host = '2001:400:a100:3010:f816:3eff:feaa:e6ec' 
        username = 'ubuntu'
        ssh_args = ['ssh', '-F','/Users/khawar/.ssh/fabric_ssh_config','-i','/Users/khawar/.ssh/sliver',f'{username}@{host}',cmd]
    else:
        print(siteName+' selected') 
        host = 'c220g5-110923.wisc.cloudlab.us' 
        username = 'ks9dw'
        #cmd = "screen -dm -S startPipelinex"         
        ssh_args = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',f'{username}@{host}',cmd]
    
    return ssh_args

def getCommand(commandOptions):
    if commandOptions == 'gpuHigh':
        cmd = "${HOME}/AVAH/scripts/run_variant_analysis_at_scale.sh -i /proj/eva-public-PG0/${USER}-sampleIDs-vlarge.txt -d NONE -n 16 -b 2 -p 1 -P H -G"
    elif commandOptions == 'cpu':
        cmd = "${HOME}/AVAH-FABRIC/scripts/run_variant_analysis_at_scale.sh -i /proj/eva-public-PG0/${USER}-sampleIDs-vlarge.txt -d NONE -n 8 -b 2 -p 17 -P H -G"
    elif commandOptions == 'gpu':
        cmd = "${HOME}/AVAH-FABRIC/scripts/run_variant_analysis_at_scale.sh -i /proj/eva-public-PG0/${USER}-sampleIDs-vlarge.txt -d NONE -n 8 -b 2 -p 17 -P H -G -g -m 2"
    elif commandOptions == 'gpuLow':      
        cmd = "${HOME}/AVAH-FABRIC/scripts/run_variant_analysis_at_scale.sh -i /proj/eva-public-PG0/${USER}-sampleIDs-vlarge.txt -d NONE -n 8 -b 2 -p 17 -P H -G -g -F"  
    return cmd  


def executeCommand(ssh_args):
    try:
        completed_process = subprocess.run(ssh_args,capture_output=True, text=True, check=True)
        output = completed_process.stdout
    
    except subprocess.CalledProcessError as e:
        output = e.stderr   
        #print(output)
                     
    return output 
            

def drive_upload(fileName):
    print("uploading")
    gauth = GoogleAuth()           
    drive = GoogleDrive(gauth)  
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)
    gfile = drive.CreateFile({'parents': [{'id': "1nK1hnETtzVl8gJuM5EdGXvh9ZWo84zgI"}]})
    gfile.SetContentFile(fileName)
    gfile.Upload() # Upload the file.

    file_id = gfile['id']
    print("File ID of the uploaded file:", file_id)

    # Set the permission for anyone with the link to download the file
    gfile.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })

    # Get the shareable link to download the file
    shareable_link = gfile['alternateLink']
    print("Shareable link:", shareable_link)
    return shareable_link
        

def run_single_node():
            host = 'clnode003.clemson.cloudlab.us' 
            username = 'ks9dw'
            
            ##start screen session with screen name 
            cmd = "screen -dm -S startPipelinex"
            ssh_args = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',f'{username}@{host}',cmd]
            #print("starting screen session..")
            #executeCommand(ssh_args)
            
            ##change working directory to /mydata
            #cmd = 'screen -S startPipelinex -X stuff "cd /mydata\n"'
            cmd = 'screen -S startPipelinex -X stuff "ls\n"'
            ssh_args = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',f'{username}@{host}',cmd]
            #print("changing directory in screen..")
            #executeCommand(ssh_args)
            
            
            cmd = '[ -e "/mydata/ERR016314_1.fastq.gz" ] && echo "1" || echo "0"'
            cmd = '[ -e "/mydata/test.txt" ] && echo "1" || echo "0"'
            ssh_args = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',f'{username}@{host}',cmd]
            
            #ret = executeCommand(ssh_args)

            
            ##run pipeline 
            # cmd = "screen -dm bash -c '${HOME}/EVA/scripts/run_variant_analysis_gatk.sh hs38 ERR016314_1.fastq.gz ERR016314_2.fastq.g; exec sh' "
            # cmd = 'screen -S startPipeline -X stuff "${HOME}/EVA/scripts/run_variant_analysis_gatk.sh hs38 ERR016314_1.fastq.gz ERR016314_2.fastq.gz\n"'
            # ssh_args = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',f'{username}@{host}',cmd]
            #executeCommand(ssh_args)
        
                
def execute_command_view(request):
    if request.method == 'POST':
        site = request.POST.get('site','') 
        genome = request.POST.get('genome', '')
        #print("genome is ",genome)
        genomeName = genome+'.vcf'
        print("Genome selected is :",genomeName)
        commandOptions = request.POST.get('command', '')
        
        execution_cmd = getCommand(commandOptions)
        ssh_args = getSiteSSH(site)
 
        return redirect('result_page/?variable='+genomeName)
                
    #return render(request, 'options_menu.html')
    return render(request, 'CIKM DEMO.html')
    #return render(request, 'command_form.html')
    


def result_page(request):            
    genomeName = request.GET.get('variable', '')
    context = {'genomeName': genomeName}
    return render(request, 'result_page.html', context)
    
    
def check_file_status(request):
    genomeName = request.GET.get('genomeName', None)
    doCheck = True
    if doCheck:
        print("Checking file status")
        #cmd = '[ -e "/mydata/"testX.txt" ] && echo "1" || echo "0"'  
        cmd = '/mydata/hadoop/bin/hdfs dfs -test -e "/{}" && echo "1" || echo "0"'.format(genomeName)
        ssh_args = getSiteSSH("cloudlab")
        ssh_args[-1] = cmd
        command_string = ' '.join(ssh_args)
        ret = subprocess.run(command_string, shell=True, executable='/bin/bash', capture_output=True, text=True, check=True)
        ret = ret.stdout
        
        #ret = executeCommand(ssh_args)
        print("ssh args are: ",ssh_args)
        print("file check command is: ",cmd)
        print("output file is :",genomeName)
        print("value of ret is :",ret)
    
    if ret[0] == "1":
        print("file found..")
        doCheck = False
        return JsonResponse({'file_exists': ret[0]})
    else:
        return JsonResponse({'file_exists': ret[0]})


def move_and_upload(request):
    genomeName = request.GET.get('genomeName', None)
    
    print("copying file from hdfs") 
    ssh_args = getSiteSSH("cloudlab")
    cmd = '/mydata/hadoop/bin/hdfs dfs -copyToLocal /{} /mydata'.format(genomeName)
    ssh_args[-1] = cmd
    command_string = ' '.join(ssh_args)
    ret = subprocess.run(command_string, shell=True, executable='/bin/bash', capture_output=True, text=True, check=True)
    ret = ret.stdout

    
    print("copying file to local")
    host = ssh_args[-2]
    cmd = "scp {}:/mydata/{} /Users/khawar/demoWebsite/homepage".format(host,genomeName)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell = True)
    except subprocess.CalledProcessError as e:
        print("Command returned non-zero exit status:", e.returncode)
        
    cmd = "python3 /Users/khawar/demoWebsite/homepage/drive_upload.py /Users/khawar/demoWebsite/homepage/{}".format(genomeName)
    print("uploading file..")
    link = subprocess.run(cmd, shell = True, capture_output= True, text= True)
    link = link.stdout.strip()
    return JsonResponse({'shareable_link':link})



def generate_shareable_link(request):
    def event_stream():
        ssh_args = getSiteSSH("cloudlab")
        print("copying file from hdfs")
        cmd = 'hdfs dfs -copyToLocal /{} /mydata'.format(genomeName)
        ssh_args[-1] = cmd
        executeCommand(ssh_args)
        host = ssh_args[-2]
        print("copying file to local")
        cmd = "scp {}:/mydata/{} /Users/khawar/demoWebsite/homepage".format(host, genomeName)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print("Command returned non-zero exit status:", e.returncode)

        print("uploading")
        cmd = "python3 /Users/khawar/demoWebsite/homepage/drive_upload.py /Users/khawar/demoWebsite/homepage/{}".format(genomeName)
        link = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        link = link.stdout.strip()

        yield "data: {}\n\n".format(link)  # Send the link as an SSE event

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response