__author__ = 'chuyiq'
'''
Simple Test on Anritsu8820
'''
import visa, os, time
import csv
rm = visa.ResourceManager()
anr = rm.open_resource('TCPIP0::10.21.141.234::56001::SOCKET', read_termination='\n')
path='/github/report/'
print(time.strftime('%d%m%Y-%H%M'))
print(anr.ask('*IDN?'))
idn=anr.ask('*IDN?')
print(anr.ask('MCIV?'))
mciv=anr.ask('MCIV?')
print(anr.ask('MCOV?'))
mcov=anr.ask('MCOV?')
time.sleep(1)
callstat=anr.ask('CALLSTAT?')
time.sleep(5)
#print(callstat)
if (callstat=='6'):
    #print(callstat)
    anr.write('CALLSO')
    time.sleep(2)
anr.write('STDSEL LTE')
anr.write('FRAMETYPE FDD')
anr.write('BANDWIDTH 10MHZ')
anr.write('BAND 1')
anr.write('DLFREQ 2140MHZ')
anr.write('ULFREQ 1950MHZ')
anr.write('MEASITEM NORMAL')
anr.write('PDSCH_P_A -3DB')
anr.write('PDSCH_P_B 1')
anr.write('INTEGRITY SNOW3G')

bwmhzlist={'1.4MHZ':1.4,'3MHZ':3,'5MHZ':5,'10MHZ':10,'15MHZ':15,'20MHZ':20}
palist={'-6DB':-6,'-4.77DB':-4.77,'-3DB':-3,'-1.77DB':-1.77,'0DB':0,'1DB':1,'2DB':2,'3DB':3}
chtypelist={'ON':'AWGN','OFF':'NONE'}
tmlist={'SINGLE':1,'CLOSED_LOOP_MULTI':4,'TX_DIVERSITY':2,'OPEN_LOOP':3}
txantlist={'SINGLE':1,'CLOSED_LOOP_MULTI':2,'TX_DIVERSITY':2,'OPEN_LOOP':2}
Fdl_low={'1':2110,'2':1930,'3':1805,'4':2110,'5':869,'6':875,'7':2620,'8':925,'9':1844.9,'10':2110,'11':1475.9,'12':728,'13':746,'14':758}
Ndl_offset={'1':0,'2':600,'3':1200,'4':1950,'5':2400,'6':2650,'7':2750,'8':3450,'9':3800,'10':4150,'11':4750,'12':5000,'13':5180,'14':5280}

#anr.write('ANTCONFIG SINGLE')
#anr.write('ANTCONFIG RX_DIVERSITY')
#anr.write('ANTCONFIG TX_DIVERSITY')

#anr.write('ANTCONFIG CLOSED_LOOP_SINanr.write('ANTCONFIG OPEN_LOOP')GLE')
#anr.write('ANTCONFIG CLOSED_LOOP_MULTI')

anr.write('OBW_MEAS ON')
anr.write('TPUT_MEAS ON')
anr.write('TPUT_SAMPLE 2000')
anr.write('CHCODING RMC')
anr.write('SCHEDULING STATIC')
#

anr.write('AWGNLVL ON')
anr.write('AWGNPWR -30')
anr.write('UECAT CAT4')

anr.write('CALLSA')
#print(callstat)
#anr.write('SWP')

print(anr.ask('BANDWIDTH?'))
bwmhz=bwmhzlist[anr.ask('BANDWIDTH?')]
print(anr.ask('STDSEL?'))
std=anr.ask('STDSEL?')
print(anr.ask('FRAMETYPE?'))
dmode=anr.ask('FRAMETYPE?')
print(anr.ask('BAND?'))
rfband=anr.ask('BAND?')
dlfreq=anr.ask('DLFREQ?')
earfcn=(float(dlfreq)/1000000-float(Fdl_low[rfband]))*10+float(Ndl_offset[rfband])
print(dlfreq)
print(anr.query('OLVL_EPRE?'))
time.sleep(2)
anr.write('TESTPRM RX_SENS')
anr.write('CQI_RANGE 15')
anr.ask('CQI_COUNT? 1,15')
anr.write('OLVL_EPRE -72.8')
anr.write('MAXHARQTX 4')
time.sleep(2)
pmi='NONE'
print(anr.ask('*OPC?'))

#anr.write('ULRMC_64QAM ENABLED')
anr.write('ULIMCS 23')
anr.write('ULRMC_RB 50')
anr.write('ULRB_START 0')
#anr.write('DLRMC_RB 50')
#anr.write('DLRB_START 0')
anr.write('DLIMCS1 28')
anr.write('DLIMCS2 28')
anr.write('DLIMCS3 28')
#anr.write('DLIMCS4 -1')
#time.sleep(15)
print(anr.ask('LVL?'))
time.sleep(5)
#print(anr.ask('OLVL_EPRE?'))

time.sleep(1)
anr.write('S2')
#anr.write('SWP')
#meast=anr.ask('SWP?')
anr.timeout=600000;

while(1):
    mea_ready=anr.ask('SWP?')
    time.sleep(1)
    if(mea_ready=='0'):
        #print(anr.ask('TPUT_BLER?'))
        print(anr.ask('TPUT? TTL'))


        #result= str(anr.ask('TPUT? TTL'))
        result= [anr.ask('TPUT? TTL')]
        timestr = time.strftime('%Y-%m-%d_%H%M%S')

        testparame=['bwmhz,dmode,rfband,earfcn,rsepre,pa,pb,chtype,snr,dlnprb,dlrbstart,ulmcs,ulnprb,ulrbstart,tm,txants,pmi, schedtype, nhrtx,riv,dlthr_Mbps,dlbler,cqi,nack,dtx,ulthr_Mpbs,ulbler,dlthr_cw1,dlthr_cw2']
        rsepre=anr.ask('OLVL_EPRE?')
        pa=palist[anr.ask('PDSCH_P_A?')]
        pb=anr.ask('PDSCH_P_B?')
        chtype=chtypelist[anr.ask('AWGNLVL?')]
        snr=0-float(anr.ask('AWGNPWR?'))
        dlnprb=anr.ask('DLRMC_RB?')
        dlrbstart=anr.ask('DLRB_START?')
        ulmcs=anr.ask('ULIMCS?')
        ulnprb=anr.ask('ULRMC_RB?')
        ulrbstart=anr.ask('ULRB_START?')
        cqi=anr.ask('CQI_RANGE?')
        dlthr_Mbps=float(anr.ask('TPUT?'))/1024.00
        ulthr_Mbps=float(anr.ask('UL_TPUT?'))/1024.00
        dlthr_cw1=float(anr.ask('TPUT_CW0?'))/1024.00
        dlthr_cw2=float(anr.ask('TPUT_CW1?'))/1024.00
        nack=anr.ask('TPUT_BLERCNTNACK?')
        dtx=anr.ask('TPUT_BLERCNTDTX?')
        dlbler=anr.ask('TPUT_BLER?')
        ulbler=anr.ask('UL_TPUT_BLER?')
        tm=tmlist[anr.ask('ANTCONFIG?')]
        txants=txantlist[anr.ask('ANTCONFIG?')]
        schedtype=anr.ask('SCHEDULING?')
        nhrtx=anr.ask('MAXHARQTX?')
        riv=' '+anr.ask('RVCODING? 1')+' '+anr.ask('RVCODING? 2')+' '+anr.ask('RVCODING? 3')+' '+anr.ask('RVCODING? 4')
        testresult=[bwmhz,',', dmode,',',rfband,',',earfcn,',',rsepre,',',pa,',',pb,',',chtype,',',snr,',',dlnprb,',',dlrbstart,',',ulmcs,',',ulnprb,',',ulrbstart,',',tm,',',txants,',',pmi,',',schedtype,',',nhrtx,',',riv,',',dlthr_Mbps,',',dlbler,',',cqi,',',nack,',',dtx,',',ulthr_Mbps,',',ulbler,',',dlthr_cw1,',',dlthr_cw2]

        #title=['Throughput(kbps),tput(%),tputCD1,tputCD1(%),tputCD2,tputCD2(%),bler,bler(EXP),error_count,nack,dtx,no_sample']
        #print(title+'\n'+result)
        f=open(path+'LTE_'+dmode+'_MT8820C_TestConf_testID_'+timestr+'.txt','w')
        f.write('Timestamp\t\t:'+timestr+'\nRAT\t\t\t:'+std+'_'+dmode+'\n'+'Testtype\t\t:'+std+'_'+dmode+'_'+chtype+'\n'+'Testerinfo\t\t:'+idn+' '+mciv+' '+mcov+'\n')
        f.close()
        with open(path+'LTE_'+dmode+'_'+'MT8820C_TestMeas_testID_'+timestr+'.csv','wb') as csvfile:
            csvwriter=csv.writer(csvfile,delimiter=' ',quotechar=' ',quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(testparame)
            csvwriter.writerow(testresult)
        anr.write('TESTPRM NORMAL')
        anr.write('CALLSO')
        anr.close()
        break
