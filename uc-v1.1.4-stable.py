#!/usr/bin/python3
# version 1.1.4
import socket
import shutil
import sys
import os
import threading

import time
from datetime import datetime
from getpass import getpass

from cryptography.fernet import Fernet

class colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'

class cOP:
    size = "333"
    file = "334"
    fileend = "335"
    directory = "336"
    transfer = "340"
    OK = "200"
    forbidden = "403"
    notfound = "404"
    chatroom = "808"
    remove = "299"
    upload = "300"
    download = "301"
    serverupdate = "302"
    ping = "303"
    backup = "304"
    sync = "305"
    listfs = "306"
    grep = "307"
    usertoken = "100"
    syn = "SYN"
    rst = "RST"
    sya = "SYA"
    ack = "ACK"
    package = "310"
    listall = "311"
    encrypt = "000"
    decrpyt = "999"

class TCPClient:

    def __init__(self, host, port):
        self.serverAddr = host
        self.serverPort = port
        self.keyfile = '/etc/ultron-server/key.txt'
        self.download = '/home/' + os.getlogin() + '/Documents/ultron-server/downloads/'
        self.package_path = '/etc/ultron-server/packages/'
        self.set_trigger = '/usr/bin/'
        self.token = ''
        self.clientSock = 0
        self.stop_thread = False
        self.thread_alive = False
        self.currSize = 0
        self.current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def print_log(self, msg):
        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{current_date_time}] {msg}')

    def request_connection(self, serverAddr, serverPort):
        # self.print_log(f'creating socket...')
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.print_log(f'requesting connection from [{serverAddr}]::[{serverPort}]')
        try:
            self.clientSock.connect((serverAddr, serverPort))
            self.print_log(f'connected succesfully. welcome to ultron!')
            return True
        except Exception as error:
            self.print_log(error)

    def encrypt_data(self, fileData):
        with open(self.keyfile, 'rb') as keyFile:
            key = keyFile.read()
        keyFile.close()
        fernet = Fernet(key)
        encryptedData = fernet.encrypt(fileData)
        return encryptedData

    def decrypt_data(self, fileData):
        with open(self.keyfile, 'rb') as keyFile:
            key = keyFile.read()
        keyFile.close()
        fernet = Fernet(key)
        decryptedData = fernet.decrypt(fileData)
        return decryptedData

    def get_size(self, dir1):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(dir1):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
            return total_size
    
    def end_check(self, dirSizeBefore, backupSize, destDir):
            currSize = self.get_size(destDir)
            if currSize == dirSizeBefore:
                actSize = backupSize
            else:
                actSize = currSize - dirSizeBefore
            if backupSize == actSize:
                return True
            else:
                return False
            
    def exec_rotation(self, i, h):
        c1 = '/'
        c2 = '|'
        c3 = '\\'
        c4 = '—'
        rotation = ''
        c1i = i % 2
        cl3 = h % 4
        if int(cl3) == 0:
            return c4
        elif float(i).is_integer():
            return c2
        elif int(c1i) == 0:
            return c1
        else:
            return c3
    
    def print_load_filestatus(self, byteSize, fileSize):
        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        percSize = int(byteSize) / int(fileSize)
        percSize *= 100
        percSize = round(percSize)
        hashtagCount = ''
        proccessOutput = ''
        percProccess = ''
        for i in range(101):
            if int(percSize) <= i:
                hashtagCount = i * '#'
                iCount = 100 - i
                proccessOutput = hashtagCount + iCount * '.'
                percProccess = f'{i}%'
                break
        outPut = f'[{current_date_time}] loading [{proccessOutput}] {percProccess}'
        print(outPut,end = '\r')


    def print_load_status(self, byteSize, fileSize, destDir, dirSizeBefore, backupSize):
        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        currSize = self.get_size(destDir)
        actSize = int(currSize) - int(dirSizeBefore)
        percSize = int(byteSize) / int(fileSize)
        percSize *= 100
        percSize = round(percSize)
        hashtagCount = ''
        percStatus = int(actSize) / int(backupSize) 
        percStatus *= 100
        percStatus = '{:.2f}'.format(percStatus)
        percStatus = f'{percStatus}%'
        proccessOutput = ''
        percProccess = ''
        for i in range(101):
            if int(percSize) <= i:
                hashtagCount = i * '#'
                iCount = 100 - i
                proccessOutput = hashtagCount + iCount * '.'
                percProccess = f'{i}%'
                break
        outPut = f'[{current_date_time}] loading [{proccessOutput}] {percProccess} || {percStatus}'
        print(outPut,end = '\r')


    def ping_request(self):
        self.print_log(f'requesting ping from [{self.serverAddr}]::[{self.serverPort}]')
        self.clientSock.send(cOP.ping.encode())
        answ = self.clientSock.recv(1024)
        ping = answ.decode()
        if ping == cOP.OK:
            self.print_log('server [' + colors.GREEN + 'online' + colors.WHITE + ']')
            self.clientSock.close()
            sys.exit
        else:
            self.print_log('server [' + colors.RED + 'offline' + colors.WHITE + ']')
            self.clientSock.close()

    def download_script(self, downloadType, downloadName, clientToken):
        self.print_log(f'requesting transfer from [{self.serverAddr}]::[{self.serverPort}]')
        self.clientSock.send(cOP.download.encode())
        time.sleep(0.5)
        clientToken = clientToken.encode()
        clientToken = self.encrypt_data(clientToken)
        self.clientSock.send(clientToken)
        resp = self.clientSock.recv(1024)
        resp = resp.decode()
        if resp == cOP.OK:
            if downloadType == 0:
                self.clientSock.send(cOP.file.encode())
                answ = self.clientSock.recv(1024)
                answ = answ.decode()
                if answ == cOP.OK:
                    fileNameEncr = downloadName.encode()
                    fileNameEncr = self.encrypt_data(fileNameEncr)
                    self.clientSock.send(fileNameEncr)
                    resp = self.clientSock.recv(1024)
                    resp = resp.decode()
                    if resp == cOP.OK:
                        filesize = self.clientSock.recv(1024)
                        filesize = self.decrypt_data(filesize)
                        filesize = filesize.decode()
                        filesize = int(filesize)
                        fileData = ''
                        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        while True:
                            fileBytes = self.clientSock.recv(1024)
                            fileBytes = fileBytes.decode()
                            fileData += fileBytes
                            self.print_load_filestatus(len(fileData), filesize)
                            if int(filesize) == int(len(fileData)):
                                print('')
                                break
                            else:
                                pass
                        fileData = fileData.encode()
                        fileData = self.decrypt_data(fileData)
                        download = self.download + downloadName
                        with open(download, 'wb') as file:
                            file.write(fileData)
                        file.close()
                        self.print_log(f'file written to {download}. closing connection')
                        self.clientSock.send(cOP.OK.encode())
                        self.clientSock.close()
                    elif resp == cOP.rst:
                        self.print_log(f'file_not_found_error: closing connection to [{self.serverAddr}]::[{self.serverPort}]')
                        self.clientSock.close()
                else: 
                    self.print_log('ERROR: wrong operand. permission denied from server')
                    self.clientSock.close()
            elif downloadType == 1:
                self.clientSock.send(cOP.directory.encode())
                transferDone = False
                answ = self.clientSock.recv(1024).decode()
                self.print_log(f'writing changes to {self.download}')
                if answ == cOP.OK:
                    dirNameEncr = downloadName.encode()
                    dirNameEncr = self.encrypt_data(dirNameEncr)
                    self.clientSock.send(dirNameEncr)
                    found = self.clientSock.recv(1024).decode()
                    if found == cOP.OK:
                        backupSize = self.clientSock.recv(1024)
                        backupSize = self.decrypt_data(backupSize)
                        backupSize = backupSize.decode()
                        dirSizeBefore = 0
                        pathName = None
                        transferVar = False
                        while not transferDone:
                            if not transferVar:
                                answ = self.clientSock.recv(1024).decode()
                            else: 
                                answ = cOP.transfer
                                transferVar = False
                            if answ == cOP.transfer or answ == cOP.file:
                                if answ == cOP.transfer:
                                    pathName = self.clientSock.recv(1024)
                                    pathName = self.decrypt_data(pathName)
                                    pathName = pathName.decode()  
                                    fileStatus = self.clientSock.recv(1024).decode()
                                else:
                                    fileStatus = cOP.file
                                if fileStatus == cOP.file:
                                    fileName = self.clientSock.recv(1024)
                                    fileName = self.decrypt_data(fileName)
                                    fileName = fileName.decode()
                                    destDir = self.download + pathName
                                    check_dir(destDir)
                                    dirSizeBefore = self.get_size(destDir)
                                    filesize = self.clientSock.recv(1024)
                                    filesize = self.decrypt_data(filesize)
                                    filesize = filesize.decode()
                                    filesize = int(filesize)
                                    fileData = ''
                                    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    self.clientSock.send(cOP.OK.encode())
                                    while True:
                                        fileBytes = self.clientSock.recv(1024)
                                        fileBytes = fileBytes.decode()
                                        fileData += fileBytes
                                        self.print_load_status(len(fileData), filesize, destDir, dirSizeBefore, backupSize)
                                        if int(filesize) == int(len(fileData)):
                                            break
                                        else:
                                            pass
                                    fileData = fileData.encode()
                                    fileData = self.decrypt_data(fileData)
                                    download = self.download + pathName + fileName
                                    with open(download, 'wb') as file:
                                        file.write(fileData)
                                    file.close()
                                    logName =  pathName + fileName
                                    log = f'[{current_date_time}] file written to {logName}.'
                                    lengthPath = len(log)
                                    if lengthPath > 146:
                                        count = 0
                                    else:
                                        count = 146 - lengthPath
                                    space = count * ' '
                                    log += space
                                    print(log)
                                    self.clientSock.send(cOP.OK.encode())
                                else:
                                    transferVar = True
                            elif answ == cOP.rst:
                                if self.end_check(dirSizeBefore, backupSize, destDir):
                                    self.print_log('job done. quitting')
                                    transferDone = True
                                    self.clientSock.close()
                                else:
                                    self.print_log('ERROR: end_check failed: download incomplete')
                            else:
                                self.print_log('SERVER_SIDE_ERROR: closing connection.')
                                self.clientSock.close()
                                transferDone = True      
                    else:
                        self.print_log(f'directory_not_fount_error: closing connection to [{self.serverAddr}]::[{self.serverPort}]')
                        self.clientSock.close()

        elif resp == cOP.forbidden:
            self.print_log('403 forbidden: invalid token')
            self.clientSock.close()
        else:
            self.print_log('server [' + colors.RED + 'offline' + colors.WHITE + ']')
            self.clientSock.close()

    def listfs(self, clientToken, oFile):
        self.print_log(f'requesting listfs from [{self.serverAddr}]::[{self.serverPort}]')
        self.clientSock.send(cOP.listfs.encode())
        time.sleep(0.2)
        clientToken = str(clientToken).encode()
        clientToken = self.encrypt_data(clientToken)
        self.clientSock.send(clientToken)
        answ = self.clientSock.recv(1024)
        answ = answ.decode()
        if answ == cOP.rst:
            self.print_log(f'connection refused by [{self.serverAddr}]::[{self.serverPort}]')
            self.clientSock.close()
        elif answ == cOP.OK:
            if oFile == 'NULL':
                self.clientSock.send(cOP.listfs.encode())
            else:
                self.clientSock.send(cOP.grep.encode())
            fragmentCount = 0
            filesize = self.clientSock.recv(1024)
            filesize = self.decrypt_data(filesize)
            filesize = filesize.decode()
            filesize = int(filesize)
            fileData = ''
            current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if filesize > 1448:
                fragmentCount = filesize / 1448
                fragmentCount += 1
            else:
                fragmentCount = 1
            for i in range(int(fragmentCount)):
                fileBytes = self.clientSock.recv(1500)
                fileBytes = fileBytes.decode()
                fileData += fileBytes
                #print(f'[{current_date_time}] recieving bytes: {len(fileData)}/{filesize}', end='\r')
                self.print_load_filestatus(len(fileData), filesize)
                if filesize == len(fileData):
                    print(f'[{current_date_time}] recieved bytes successfully     ', end='\r')
                    break
            fileData = fileData.encode()
            fileData = self.decrypt_data(fileData)
            fileData = fileData.decode()
            if oFile == "NULL":
                self.print_log('recieved filesystem:\r\n')
                print(fileData)
            else:
                with open(self.download + oFile, 'w') as file:
                    file.write(fileData)
                file.close()
                space = 120 * " "
                self.print_log(f'filesystem written to {self.download + oFile}{space}')
            self.clientSock.send(cOP.OK.encode())
            self.clientSock.close()

    def test_authtoken(self, clientToken):
        self.print_log(f'requesting token integrity from [{self.serverAddr}]::[{self.serverPort}]')
        self.clientSock.send(cOP.usertoken.encode())
        clientToken = str(clientToken).encode()
        clientToken = self.encrypt_data(clientToken)
        self.clientSock.send(clientToken)
        integrity = self.clientSock.recv(1024)
        integrity = integrity.decode()
        if integrity == cOP.OK:
            self.print_log('auth_token valid')
            self.clientSock.close()
        elif integrity == cOP.rst:
            self.print_log('auth_token invalid. Please contact the administrator for a new token')
            self.clientSock.close()
        else:
            self.print_log('could not answer request. closing connection')
            self.clientSock.close()

    def updatedb(self):
        self.print_log(f'updating db from [{self.serverAddr}]::[{self.serverPort}]')
        self.clientSock.send(cOP.serverupdate.encode())
        filesize = self.clientSock.recv(1024)
        filesize = self.decrypt_data(filesize)
        filesize = filesize.decode()
        filesize = int(filesize)
        fileData = ''
        while True:
            fileBytes = self.clientSock.recv(1024)
            fileBytes = fileBytes.decode()
            fileData += fileBytes
            self.print_load_filestatus(len(fileData), filesize)
            if int(filesize) == int(len(fileData)):
                break
            else:
                pass
        fileData = fileData.encode()
        fileData = self.decrypt_data(fileData)
        fileData = fileData.decode()
        with open('/usr/bin/uc', 'w') as file:
            file.write(fileData)
        file.close()
        self.print_log('\nupdated successfully')
        self.clientSock.close()

    def upload_script(self, fileDirectory, userFile, userToken):
        self.print_log(f'requesting file transfer from [{self.serverAddr}]::[{self.serverPort}]')
        self.clientSock.send(cOP.upload.encode())
        time.sleep(0.4)
        userToken = str(userToken).encode()
        userToken = self.encrypt_data(userToken)
        self.clientSock.send(userToken)
        answ = self.clientSock.recv(1024)
        answ = answ.decode()
        if answ == cOP.OK:
            current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'[{current_date_time}] sending file...', end='\r')
            # sending fileDirectory
            time.sleep(0.2)
            fileDirectory = str(fileDirectory).encode()
            fileDirectory = self.encrypt_data(fileDirectory)
            self.clientSock.send(fileDirectory)
            with open(userFile, 'rb') as file:
                data = file.read()
            file.close()
            data = self.encrypt_data(data)
            # sending filesize
            fileSize = len(data)
            fileSize = str(fileSize).encode()
            fileSize = self.encrypt_data(fileSize)
            self.clientSock.send(fileSize)
            time.sleep(0.4)
            self.clientSock.send(data)
            answ = self.clientSock.recv(1024)
            if answ.decode() == cOP.OK:
                self.print_log('sending file   done')
                self.clientSock.close()
            elif answ.decode() == cOP.rst:
                self.print_log('sending file   failed')
            else:
                self.print_log('could not resolve answer from server. quitting')
                self.clientSock.close()
        elif answ == cOP.rst:
            self.print_log('permission denied: token_invalid')
            self.clientSock.close()
        else:
            self.print_log('could not resolve answer from server. quitting')
            self.clientSock.close()

    def remove_script(self, removeName, userToken):
        self.print_log(f'requesting removal from [{self.serverAddr}]::[{self.serverPort}]')
        self.clientSock.send(cOP.remove.encode())
        time.sleep(0.2)
        userToken = str(userToken).encode()
        userToken = self.encrypt_data(userToken)
        self.clientSock.send(userToken)
        answ = self.clientSock.recv(1024)
        answ = answ.decode()
        if answ == cOP.OK:
            removePath = removeName
            removeName = removeName.encode()
            removeName = self.encrypt_data(removeName)
            self.clientSock.send(removeName)
            answ = self.clientSock.recv(1024).decode()
            if answ == cOP.OK:
                self.print_log(f'removed {removePath}')
                self.clientSock.close()
            elif answ == cOP.notfound:
                self.print_log(f'ERROR: file_not_found_error: could not locate {removePath}')
                self.clientSock.close()

    def backup_script(self, srcDirectory, dstDirectory, clientToken):
        
        def get_size(dir1):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(dir1):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
            return total_size
        
        def print_loading_backup():
            h = 4
            i = 2.5
            while True:
                rot = self.exec_rotation(i, h)
                h += 1
                i += 0.5
                print('[' + self.current_date_time + '] preparing backup ', rot, end='\r')
                if self.stop_thread:
                    break
                
        def print_punct():
            while True:
                if self.stop_thread:
                    break
                print(f'[{self.current_date_time}]', 'sending files .    (', self.currSize,'%)', end='\r')
                time.sleep(0.5)
                print(f'[{self.current_date_time}]', 'sending files ..   (', self.currSize,'%)', end='\r')
                time.sleep(0.5)
                print(f'[{self.current_date_time}]', 'sending files ...  (', self.currSize,'%)', end='\r')
                time.sleep(0.5)
                print(f'[{self.current_date_time}]', 'sending files      (', self.currSize,'%)', end='\r')
                time.sleep(0.5)
        
        def print_process(sentBytes):
            self.stop_thread = False
            current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dirSize = get_size(srcDirectory)
            self.currSize = sentBytes / dirSize * 100
            self.currSize = '{:.2f}'.format(self.currSize)
            if self.thread_alive:
                pass
            else:
                punct = threading.Thread(target=print_punct)
                punct.start()
                self.thread_alive = True
            if float(self.currSize) == 100.00:
                self.stop_thread = True
                self.thread_alive = False

        def send_backup():
            sentBytes = 0
            self.print_log(f'requesting file transfer from [{self.serverAddr}]::[{self.serverPort}]')
            self.clientSock.send(cOP.backup.encode())
            time.sleep(0.2)
            userToken = str(clientToken).encode()
            userToken = self.encrypt_data(userToken)
            self.clientSock.send(userToken)
            answ = self.clientSock.recv(1024)
            answ = answ.decode()
            if answ == cOP.OK:
                rot = threading.Thread(target=print_loading_backup)
                rot.start()
                # sending dstDirectory to server
                dstDirEncr = str(dstDirectory).encode()
                dstDirEncr = self.encrypt_data(dstDirEncr)
                self.clientSock.send(dstDirEncr)
                time.sleep(0.2)
                # checking directory
                if os.path.exists(str(srcDirectory)):
                    pass
                else:
                    self.print_log(f'ERROR: could not locate {srcDirectory}')
                    self.clientSock.close()
                    sys.exit()
                # sending backupsize
                backupSize = get_size(srcDirectory)
                backupSize = str(backupSize).encode()
                backupSize = self.encrypt_data(backupSize)
                self.clientSock.send(backupSize)
                time.sleep(0.2)
                srcDirectoryEncr = srcDirectory.encode()
                srcDirectoryEncr = self.encrypt_data(srcDirectoryEncr)
                self.clientSock.send(srcDirectoryEncr)
                time.sleep(0.2)                
                # fetching files and dirnames from srcDirectory and sending them to server
                cut = len(srcDirectory)
                for dirpath, dirnames, files in os.walk(srcDirectory):
                    # sending status
                    time.sleep(0.2)
                    self.clientSock.send(cOP.backup.encode())
                    # sending directory name
                    dirpath = dirpath + '/'
                    dirpathEncr = str(dirpath).encode()
                    dirpathEncr = self.encrypt_data(dirpathEncr)
                    self.clientSock.send(dirpathEncr)
                    time.sleep(0.2)
                    for fileName in files:
                        # sending fileOperand
                        time.sleep(0.2)
                        self.clientSock.send(cOP.file.encode())
                        # sending fileName
                        fileNameEncr = str(fileName).encode()
                        fileNameEncr = self.encrypt_data(fileNameEncr)
                        time.sleep(0.2)
                        self.clientSock.send(fileNameEncr)
                        with open(dirpath + fileName, 'rb') as fileOpen:
                            fileBytes = fileOpen.read()
                        fileOpen.close()
                        # sending fileSize
                        fileSize = len(fileBytes)
                        fileSize = str(fileSize).encode()
                        fileSize = self.encrypt_data(fileSize)
                        time.sleep(0.2)
                        self.clientSock.send(fileSize)
                        time.sleep(0.2)
                        # printing process
                        sentBytes += len(fileBytes)
                        self.stop_thread = True
                        rot.join()
                        print_process(sentBytes)
                        # sending bytes
                        fileBytes = self.encrypt_data(fileBytes)
                        # sending filesize
                        fileBytesSize = len(fileBytes)
                        fileBytesSize = str(fileBytesSize).encode()
                        fileBytesSize = self.encrypt_data(fileBytesSize)
                        self.clientSock.send(fileBytesSize)
                        time.sleep(0.2)
                        self.clientSock.send(fileBytes)
                        time.sleep(0.3)
                        # waiting for OK from server
                        status = self.clientSock.recv(1024)
                        status = status.decode()
                        if status == cOP.OK:
                            pass
                        else:
                            self.print_log(f'message from server: {status}')
                self.clientSock.send(cOP.OK.encode())
                time.sleep(0.2)
                endCheck = self.clientSock.recv(1024)
                endCheck = endCheck.decode()
                if endCheck == cOP.OK:
                    self.print_log('backup completed. quitting      ')
                    self.clientSock.close()
                    sys.exit()
                else:
                    self.print_log(f'message from server: {endCheck}')
                    self.clientSock.close()
            elif answ == cOP.rst():
                self.print_log('connection refused')
                self.clientSock.close()
            else:
                self.print_log('could not resolve response. QUITTING')
                self.clientSock.close()
        try:
            send_backup()
        except Exception as e:
            print(e)
    
    def crypt(self):
        self.print_log("---encryption/decryption mode---")
        key = getpass("Enter key: ")
        key = key.encode()
        key = self.encrypt_data(key)
        answ = input("Do you want to (e)ncrypt or (d)ecrypt your data? »» ")
        if answ in "d, D":
            self.print_log("Decrypting your data. This may take a while...")
            self.clientSock.send(cOP.decrpyt.encode())
            time.sleep(0.3)
            self.clientSock.send(key)
        elif answ in "e, E":
            self.print_log("Encrypting your data. This may take a while...")
            self.clientSock.send(cOP.encrypt.encode())
            time.sleep(0.3)
            self.clientSock.send(key)
        else:
            sys.exit("ERROR: invalid option detected")
        recv = self.clientSock.recv(1024)
        recv = recv.decode()
        self.print_log(recv)
        self.clientSock.close()
            
    def install(self, userToken, package):
        def install_package(package):
            package_path_complete = self.package_path + package + '/'
            setup_path = package_path_complete + 'setup.py'
            self.print_log('installing triggers')
            shutil.copy(package_path_complete + package, '/usr/bin/' + package)
            os.system(f'chmod +x /usr/bin/{package}')
            if os.path.exists(setup_path):
                self.print_log('running setup.py')
                os.system('python3 ' + setup_path) 
            else:
                pass
        self.print_log(f'installing package from [{self.serverAddr}]::[{self.serverPort}]')
        self.clientSock.send(cOP.package.encode())
        time.sleep(0.2)
        userToken = str(userToken).encode()
        userToken = self.encrypt_data(userToken)
        self.clientSock.send(userToken)
        answ = self.clientSock.recv(1024)
        answ = answ.decode()
        if answ == cOP.OK:
            pkgencr = package.encode()
            pkgencr = self.encrypt_data(pkgencr)
            self.clientSock.send(pkgencr)
            answ = self.clientSock.recv(1024).decode()
            if answ != cOP.OK:
                self.print_log(f'requested package {package} not found')
            else:
                check_dir(self.package_path + package + '/')
                pkgsize = self.clientSock.recv(1024)
                pkgsize = self.decrypt_data(pkgsize)
                pgksize = pkgsize.decode()
                transferDone = False
                transferVar = False
                current_package_size = 0
                i = 2.5
                h = 4
                while not transferDone:
                    if not transferVar:
                        answ = self.clientSock.recv(1024).decode()
                    else: 
                        answ = cOP.transfer
                        transferVar = False
                    if answ == cOP.transfer or answ == cOP.file:
                        if answ == cOP.transfer:
                            pathName = self.clientSock.recv(1024)
                            pathName = self.decrypt_data(pathName)
                            pathName = pathName.decode()  
                            check_dir('/etc/' + pathName)
                            fileStatus = self.clientSock.recv(1024).decode()
                        else:
                            fileStatus = cOP.file
                        if fileStatus == cOP.file:
                            fileName = self.clientSock.recv(1024)
                            fileName = self.decrypt_data(fileName)
                            fileName = fileName.decode()
                            destDir = self.package_path + package + '/'
                            dirSizeBefore = self.get_size(destDir)
                            filesize = self.clientSock.recv(1024)
                            filesize = self.decrypt_data(filesize)
                            filesize = filesize.decode()
                            filesize = int(filesize)
                            fileData = ''
                            current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            self.clientSock.send(cOP.OK.encode())
                            while True:
                                fileBytes = self.clientSock.recv(1024)
                                fileBytes = fileBytes.decode()
                                fileData += fileBytes
                                current_package_size += len(fileData)
                                currSize = (int(current_package_size)/int(pkgsize))*100
                                percsize = '{:.2f}'.format(currSize)
                                rotation = self.exec_rotation(i, h)
                                h += 1
                                i += 0.5
                                print('[' + self.current_date_time + ']' + ' loading package ' + rotation, end=('\r'))
                                if int(filesize) == int(len(fileData)):
                                    break
                                else:
                                    pass
                            fileData = fileData.encode()
                            fileData = self.decrypt_data(fileData)
                            download = '/etc/' + pathName + fileName
                            with open(download, 'wb') as file:
                                file.write(fileData)
                            file.close()
                            self.clientSock.send(cOP.OK.encode())
                        else:
                            transferVar = True
                    elif answ == cOP.rst:
                        #if self.end_check(dirSizeBefore, pkgsize, destDir):
                        self.print_log('package download complete')
                        transferDone = True
                        self.clientSock.close()
                        install_package(package)
                        self.print_log(f'[+] package {package} installed successfully.')
                        #else:
                        #    self.print_log('ERROR: end_check failed: download incomplete')
                    else:
                        self.print_log('SERVER_SIDE_ERROR: closing connection.')
                        self.clientSock.close()
                        transferDone = True         
        else:
            self.print_log(f'{package} package not found.')
            self.clientSock.close()      

    def listall(self, userToken): 
        self.print_log(f'listing available packages from [{self.serverAddr}]::[{self.serverPort}]')
        self.clientSock.send(cOP.listall.encode())
        time.sleep(0.2)
        userToken = str(userToken).encode()
        userToken = self.encrypt_data(userToken)
        self.clientSock.send(userToken)
        answ = self.clientSock.recv(1024)
        answ = answ.decode()
        endData = ''.encode()
        if answ == cOP.OK:
            while True:
                data = self.clientSock.recv(1024)
                endData += data
                if len(data) < 1024:
                    break
            data = self.decrypt_data(endData)
            data = data.decode()
            print(data)
            self.clientSock.close()
            sys.exit()    
        else:
            self.print_log("invalid token")
            sys,exit()
    
    def check_install(self,package):
        if os.path.exists(self.package_path + package):
            self.print_log(f"[*] package {package} already installed.")
            sys.exit()
        else:
            pass
        
    def remove(self, package):
        try:
            shutil.rmtree(self.package_path + package)
            os.remove("/usr/bin/" + package)
            self.print_log(f"[*] removed package {package} succesfully.")   
        except PermissionError:
            self.print_log('ERROR: Permission denied. Are you root?')
        except Exception as e:
            self.print_log(f'ERROR: {package} package not found.')
            
            
    def client_start(self):
        try:
            return self.request_connection(self.serverAddr, self.serverPort)
        except KeyboardInterrupt:
            sys.exit('^C')
        except Exception as error:
            self.print_log(error)
            sys.exit()
            

def help_menu():
        print("""
version 1.1.4
    uc server instructions: 
usage: uc <operands> [INPUT]  
    --auth [TOKENFILE]      # checks token validation
    --b [SRC_DIR, DST_DIR]  # backup script 
    --updateuc              # updates client to latest version
    --updateuc-devops       # only for developer
    --d -f [FILE]           # downloads selected file
    --d -r [DIR]            # downloads selected directory
    --listfs --o [FILE]     # lists complete filesystem    
    --p                     # ping request 
    --r [FILE/DIR]          # remove script
    --sync                  # synchronises all data 
    --u [DEST_PATH, FILE]   # uploads selected file
    --c                     # encryption/decryption mode
    
    uc package installer:
usage: uc <options> [PACKAGE]
    install  # installs the requested package if available 
    remove   # removes the selected package from system
    update   # updates the selected package
    search   # checks if the package is available
    list-all # lists all packages including their current development status
    sync     # synchronises all packages 
            """)

def check_dir(dirPath):
    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if os.path.exists(str(dirPath)):
        #self.print_log(f'Directory {dirPath} exists.')
        pass
    else:
        print(f'[{current_date_time}] Directory {dirPath} does not exist --> creating...')
        os.makedirs(dirPath)

def operand_unsupported():
    print('Sorry. This feature is still in development and currently unavailable.')
    sys.exit()

def recieve_token(tokenfile):
    with open(tokenfile, 'r') as file:
        token = file.read()
    file.close()
    return token


opList = [
    "-h", "--h", "-help", "--h","--r","--d", "--p", "--b", "--u", "--updateuc", "--auth", "--listfs",
    '--updateuc-devops','install', 'remove', 'search', 'update', 'list-all', 'sync', "--c"
]

def client_start():
    tokenfile = '/etc/ultron-server/token.txt'
    token = recieve_token(tokenfile)
    configfile = '/etc/ultron-server/config.csv'
    # extract/create server configuration
    serverport = 0
    serveraddr = ''
    if os.path.exists(configfile):
        with open(configfile, 'r') as configFile:
            ultronConfig = configFile.read()
        configFile.close()
        comma = ','
        commaPos = []
        for pos, char in enumerate(ultronConfig):
            if (char == comma):
                commaPos.append(pos)        
        serveraddr = str(ultronConfig[commaPos[0]+1:commaPos[1]])
        serverport = str(ultronConfig[commaPos[1]+1:commaPos[2]])
    else:
        print("---server configuration---")
        serveraddr = input("enter server address: ")
        serverport = input("enter server port: ")
        check_dir('/etc/ultron-server')
        with open(configfile, 'w') as configFile:
            configFile.write(',' + str(serveraddr) + ',' + str(serverport) + ',')
        configFile.close()
        print("configuration written to ", configfile)
    
    client = TCPClient(serveraddr, int(serverport))   
    sysnumberone = 1
    sysnumbertwo = 2
    sysnumberthree = 3
    if len(sys.argv) == 0:
            help_menu()
    elif sys.argv[sysnumberone] in opList:
        if sys.argv[sysnumberone] == 'remove':
            package = sys.argv[sysnumbertwo]
            try:
                client.remove(package)
            except KeyboardInterrupt:
                sys.exit("\r\n")
            sys.exit()
        elif sys.argv[sysnumberone] == 'install':
            package = sys.argv[sysnumbertwo]
            try:
                client.check_install(package)
            except KeyboardInterrupt:
                sys.exit("\r\n")
            pass        
        if sys.argv[sysnumberone] in ("-help", "-h", "--help", "--h"):
            help_menu()
            sys.exit()
        if client.client_start():
            if sys.argv[sysnumberone] == "--d":
                downloadType = sys.argv[sysnumbertwo]
                if downloadType in ("-f", "-r"):
                    downloadName = sys.argv[sysnumberthree]
                    if downloadType == "-f":
                        downloadType = 0
                    else:
                        downloadType = 1
                else: 
                    help_menu()
                try:
                    client.download_script(downloadType, downloadName, token)
                except KeyboardInterrupt:
                    sys.exit("\r\n^C")
                    
            elif sys.argv[sysnumberone] == "--p":
                try:
                    client.ping_request()
                except KeyboardInterrupt:
                    sys.exit("\r\n")
                    
            elif sys.argv[sysnumberone] == "--b":
                backup = sys.argv[sysnumbertwo]
                destDir = sys.argv[sysnumberthree]
                try:
                    client.backup_script(backup, destDir, token)
                except KeyboardInterrupt:
                    sys.exit("\r\n")

            elif sys.argv[sysnumberone] == "--u":
                upload = sys.argv[sysnumbertwo]
                file = sys.argv[sysnumberthree]
                try:
                    client.upload_script(upload, file, token)
                except KeyboardInterrupt:
                    sys.exit("\r\n")

            elif sys.argv[sysnumberone] == "--r":
                removeName = sys.argv[sysnumbertwo]
                try:
                    client.remove_script(removeName, token)
                except KeyboardInterrupt:
                    sys.exit('\r\n')

            elif sys.argv[sysnumberone] == "--updateuc":
                try:
                    client.updatedb()
                except KeyboardInterrupt:
                    sys.exit("\r\n")
                    
            elif sys.argv[sysnumberone] == "--updateuc-devops":
                try:
                    os.system('uc --u /ultron-server/uc /usr/bin/uc ')
                except KeyboardInterrupt:
                    sys.exit("\r\n")                
                    
            elif sys.argv[sysnumberone] == "--auth":
                tokenFile = sys.argv[sysnumbertwo]
                with open(tokenFile, "r") as tf:
                    token = tf.read()
                tf.close()
                try:
                    client.test_authtoken(token)
                except KeyboardInterrupt:
                    sys.exit("\r\n")
                    
            elif len(sys.argv) == 4 and sys.argv[sysnumberone] == "--listfs" and sys.argv[sysnumbertwo] == "--o":
                oFile = sys.argv[sysnumberthree]
                try:
                    client.listfs(token, oFile)
                except KeyboardInterrupt:
                    sys.exit("\r\n")

            elif sys.argv[sysnumberone] == "--listfs":
                oFile = "NULL"
                try:
                    client.listfs(token, oFile)
                except KeyboardInterrupt:
                    sys.exit("\r\n")
            
            elif sys.argv[sysnumberone] == 'install':
                package = sys.argv[sysnumbertwo]
                try:
                    client.install(token, package)
                except KeyboardInterrupt:
                    sys.exit("\r\n")
            
            elif sys.argv[sysnumberone] == 'update':
                package = sys.argv[sysnumbertwo]
                try:
                    client.update(token, package)
                except KeyboardInterrupt:
                    sys.exit("\r\n")
            
            elif sys.argv[sysnumberone] == 'list-all':
                try:
                    client.listall(token)
                except KeyboardInterrupt:
                    sys.exit("\r\n")
            
            elif sys.argv[sysnumberone] == 'sync':
                operand_unsupported          
            
            elif sys.argv[sysnumberone] == 'search':
                package = sys.argv[sysnumbertwo]
                try:
                    client.search(token, package)
                except KeyboardInterrupt:
                    sys.exit("\r\n")  
            
            elif sys.argv[sysnumberone] == 'remove':
                package = sys.argv[sysnumbertwo]
                try:
                    client.remove(token, package)
                except KeyboardInterrupt:
                    sys.exit("\r\n") 
            elif sys.argv[sysnumberone] == "--c":
                try:
                    client.crypt()
                except KeyboardInterrupt:
                    sys.exit("\r\n")                 

    else:
        help_menu()


#client_start() # debugg 

try:
    client_start()
except Exception as error:
    if str(error) == '':
        error = 'unknown'
    print('\r\nSYS_ERROR: ', str(error))


    
