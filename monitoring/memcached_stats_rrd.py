#!/usr/bin/env python
#  omkar dhualp 2016
#    - monitors and graphs stats from memcached or membase
#    - stores data in RRD (round-robin database)
#    - generates .png images of plots/stats
#    - run this script at regular intervals with a task/job scheduler
#    - requires python 2.x, python-memcached, rrdtool



import memcache
import os.path
import subprocess
import sys
import time
import traceback



# Config Settings
NODES = ('127.0.0.1:11211') 
INTERVAL = 60  # secs
STATS = (
    ('get_hits', 'GAUGE'),
    ('get_misses', 'GAUGE'),
    ('evictions', 'GAUGE'),
    ('bytes_written', 'DERIVE'),
    ('curr_connections', 'GAUGE')
)  # (stat name, rrd datasource type)
GRAPH_MINS = (60, 180)  # timespans for graph/png files
GRAPH_DIR = '/var/www/fakingmonkey/'  # output directory



def main():
    print 'connecting to memcached...'

    try:
        mc = memcache.Client(NODES)
        all_stats = mc.get_stats()
        print all_stats
    except Exception:
        print time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()), 'error'
        traceback.print_exc()
        sys.exit(1)
        
    for node_stats in all_stats:
        for (stat, datasource_type) in STATS:
            server, stats = node_stats
            host = server.split(':')[0]
            rrd_name = '%s_%s.rrd' % (host, stat)
            rrd = RRD(rrd_name, host, stat)
            rrd.graph_dir = GRAPH_DIR
            if not os.path.exists(rrd_name):
                rrd.create(INTERVAL, datasource_type)
            value = stats[stat]
            print time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()), host, stat, value
            rrd.update(value)
            for mins in GRAPH_MINS:
                rrd.graph(mins)
        


class RRD(object):
    def __init__(self, rrd_name, node, stat):
        self.node = node
        self.stat = stat
        self.rrd_name = rrd_name
        self.rrd_exe = 'rrdtool'
        self.graph_dir = ''        
        self.graph_width = 480
        self.graph_height = 160
        

    def create(self, interval, ds_type='GAUGE'):  
        interval = str(interval) 
        interval_mins = float(interval) / 60  
        heartbeat = str(int(interval) * 2)
        ds_string = ' DS:ds:%s:%s:0:U' % (ds_type, heartbeat)
        cmd_create = ''.join((self.rrd_exe, 
            ' create ', self.rrd_name, ' --step ', interval, ds_string,
            ' RRA:AVERAGE:0.5:1:', str(int(4000 / interval_mins)),
            ' RRA:AVERAGE:0.5:', str(int(30 / interval_mins)), ':800',
            ' RRA:AVERAGE:0.5:', str(int(120 / interval_mins)), ':800',
            ' RRA:AVERAGE:0.5:', str(int(1440 / interval_mins)), ':800'))
        cmd_args = cmd_create.split(' ')
        p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        cmd_output = p.stdout.read()
        if len(cmd_output) > 0:
            raise RRDException('unable to create RRD: %s' % cmd_output.rstrip())
        
  
    def update(self, value):
        cmd_update = '%s update %s N:%s' % (self.rrd_exe, self.rrd_name, value)
        cmd_args = cmd_update.split(' ')
        p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        cmd_output = p.stdout.read()
        if len(cmd_output) > 0:
            raise RRDException('unable to update RRD: %s' % cmd_output.rstrip())
    
    
    def graph(self, mins):       
        start_time = 'now-%s' % (mins * 60)  
        output_filename = '%s_%i.png' % (self.rrd_name, mins)
        end_time = 'now'
        cur_date = time.strftime('%m/%d/%Y %H\:%M\:%S', time.localtime())    
        cmd = [self.rrd_exe, 'graph', self.graph_dir + output_filename]
        cmd.append('COMMENT:\\s')
        cmd.append('COMMENT:%s    ' % cur_date)
        cmd.append('DEF:ds=%s:ds:AVERAGE' % self.rrd_name)
        cmd.append('AREA:ds#FF6666:%s  ' % self.stat)
        cmd.append('VDEF:dslast=ds,LAST')
        cmd.append('VDEF:dsavg=ds,AVERAGE')
        cmd.append('VDEF:dsmin=ds,MINIMUM')
        cmd.append('VDEF:dsmax=ds,MAXIMUM')
        cmd.append('COMMENT:\\s')
        cmd.append('COMMENT:\\s')
        cmd.append('COMMENT:\\s')
        cmd.append('COMMENT:\\s')
        cmd.append('GPRINT:dslast:last %.1lf%S    ') 
        cmd.append('GPRINT:dsavg:avg %.1lf%S    ')
        cmd.append('GPRINT:dsmin:min %.1lf%S    ')
        cmd.append('GPRINT:dsmax:max %.1lf%S    ')
        cmd.append('COMMENT:\\s')
        cmd.append('COMMENT:\\s')
        cmd.append('--title=Memcached Node %s' % self.node)
        cmd.append('--vertical-label=%s' % self.stat)
        cmd.append('--start=%s' % start_time)
        cmd.append('--end=%s' % end_time)
        cmd.append('--width=%i' % self.graph_width)
        cmd.append('--height=%i' % self.graph_height)
        cmd.append('--slope-mode')
        cmd.append('--lower-limit=0')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        cmd_output = p.stdout.read()
        if len(cmd_output) > 10:
            raise RRDException('unable to graph RRD: %s' % cmd_output.rstrip())
            
          
          
class RRDException(Exception): pass

    
    
if __name__ == '__main__':
    main()
