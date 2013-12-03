#!/usr/bin/perl

####
### v 0.5
#####
### ## changelog ###
### 
### 0.5 * fixed a bug that caused nastry crash if the nc binary was not avaliable / 27 Aug 2012
### 0.4 * fixed bug that messed up version numbers since repcached_version was introduced
### 0.3 * fixed bug that messed up totals for multiple servers on the same host
###	* added bytes read/written per second in MB and totlta / 13 May 2011
### 0.2 added totals below columns and other small changes / 27 Nov 2009
### 0.1 initial version / 23 Oct 2009
### http://code.google.com/p/memcmon/
####
### license GPLv3 -> http://www.gnu.org/licenses/gpl.html
####


use strict;
use Curses;
use Time::HiRes qw(gettimeofday tv_interval usleep);

# enter memcahed IPs below
# if :port not supplied - assume :11211
my @memc = qw(
53.212.250.133:11211
);

$| = 1;

# check if nc is avaliable

my $nc_valid = 0;
my $nc_path = `which nc 2>/dev/null`;
chomp $nc_path;

if ($nc_path) {
	my $nc_mime = `file -i $nc_path| grep -e "application\/x-executable" -e "symlink" 2>/dev/null`;
	chomp $nc_mime;
	$nc_valid = 1 if $nc_mime;
}

if ($nc_valid == 0) {
	print "sorry, could not find the 'nc' application, please install it and try again\n";
	exit;
}

my (
$what, 
$howmuch, 
$uptime, 
$version, 
$curr_connections, 
$threads, 
$curr_items, 
$curr_items_change, 
$curr_bytes_read,
$bytes,
$bytes_read, 
$bytes_written,
$limit_maxbytes, 
$server, 
$get_hitsps, 
$get_missesps, 
$usage_percentage,
$total_conns,
$total_get_hitsps,
$total_get_missps,
$total_bytes,
$total_limit_maxbytes,
$total_items_cached,
$total_items_change,
$total_bytes_read,
$total_bytes_written,
$start_time,
$end_time,
$elapsed_time,
%tmp_stats,
$cnt,
);

my @str = ('a'..'z', '1..9', 'A'..'Z');
my $tmpfile = '/tmp/';
for (1..15) {
	$tmpfile .= $str[int(rand($#str))];
}
undef @str;
open TMP_FILE, ">$tmpfile";
print TMP_FILE "\n";
close TMP_FILE;

initscr();
curs_set(0);

$SIG{INT} = \&ctrlc;
sub ctrlc {
	$SIG{INT} = \&ctrlc;
	warn "\n\tQuit you say....? ok...\n";
	sleep 1;
	unlink $tmpfile or warn "could not remove $tmpfile : $!\n";
	system('reset');
	exit;
}

while (1) {
	$start_time = [gettimeofday];
	$total_get_hitsps	= 0;
	$total_get_missps	= 0;
	$total_items_cached	= 0;
	$total_items_change	= 0;
	$total_conns		= 0;
	$total_bytes		= 0;
	$total_limit_maxbytes	= 0;
	$total_bytes_read 	= 0;
	$total_bytes_written	= 0;
	$cnt = 3;
	addstr($cnt++, 5, "memcmon v0.5");
	addstr(++$cnt, 5, "server                  curr     gets   misses  cache    usage  usage    items   items   bytes    bytes     threads uptime  version  ");
	addstr(++$cnt, 5, "  IP                    conns    per/s  per/s  size(MB)  (MB)    (%)     cached  change  read(MB) write(MB)          in h            ");
	addstr(++$cnt, 5, "=====================================================================================================================================");

	`echo >> $tmpfile`;
	
	open RO, "<$tmpfile";
	while (<RO>) {
			start_color();
		if (/err/) {
			init_pair(3,1,0); 
			attron(COLOR_PAIR(3)); 
			addstr(++$cnt, 5, $_);
			attroff(COLOR_PAIR(3));
		} else {
			init_pair(4,2,0);
                        attron(COLOR_PAIR(4));
                        addstr(++$cnt, 5, $_);
                        attroff(COLOR_PAIR(3)); 
		}


	}
	close RO;
	unlink "$tmpfile";
	open FILE, ">>$tmpfile";
	foreach (@memc) {
		$server = $_;
		$curr_connections = "err";
		my ($server_t, $port) = split /:/, $server;
		$port = 11211 unless $port;
		my @stats = `echo stats | nc -w 1 $server_t $port 2>/dev/null`;
		$uptime = $bytes = $usage_percentage = $bytes
		= $version = $get_hitsps = $curr_items_change
		= $curr_connections  = $get_missesps
		= $threads = $limit_maxbytes = $curr_items = $bytes_read = $bytes_written
		= "err" if $?;
		foreach (@stats) {
			(undef, $what, $howmuch) = split / /, $_;
			if ($what =~ /uptime/) {
				$uptime = $howmuch;
				$uptime /= 3600;
				$uptime = int($uptime);
			}
			elsif ($what eq "version") {
				$version = $howmuch;
			}
			elsif ($what eq "curr_connections") {
				$curr_connections = $howmuch;
				$total_conns += $howmuch;
			}
			elsif ($what eq "threads") {
				$threads = $howmuch;
			}
			elsif ($what eq "get_hits") {		
				$get_hitsps = $howmuch;
				$get_hitsps -= $tmp_stats{"$server get_hits"};
				$tmp_stats{"$server get_hits"} = $howmuch;
				$total_get_hitsps += $get_hitsps;
			}
			elsif ($what eq "get_misses") {
				$get_missesps = $howmuch;
				$get_missesps -= $tmp_stats{"$server get_miss"};
				$tmp_stats{"$server get_miss"} = $howmuch;
				$total_get_missps += $get_missesps;
			}
			elsif ($what eq "limit_maxbytes") {
				$limit_maxbytes = $howmuch;
				$limit_maxbytes /= 1024*1024;
				$limit_maxbytes = int($limit_maxbytes);
				$total_limit_maxbytes += $limit_maxbytes;
			}
			elsif ($what eq "bytes") {
				$bytes = $howmuch;
				$bytes /= 1024*1024;
				$total_bytes += $bytes;
				$usage_percentage = $bytes/$limit_maxbytes*100;
			}
			elsif ($what eq "curr_items") {
				$curr_items = $howmuch;
				$total_items_cached += $curr_items;
				$curr_items_change = $howmuch;
				$curr_items_change -= $tmp_stats{"$server curr_items"};
				$total_items_change += $curr_items_change;
				$curr_items_change = "+" . $curr_items_change if $curr_items_change =~ /^\d/;
				$tmp_stats{"$server curr_items"} = $howmuch;
			}
			elsif ($what eq "bytes_read") {
                                $bytes_read = $howmuch;
                                $bytes_read -= $tmp_stats{"$server bytes_read"};
                                $tmp_stats{"$server bytes_read"} = $howmuch;
				$bytes_read /= 1024*1024;
				$total_bytes_read += $bytes_read;
			}
			elsif ($what eq "bytes_written") {
                                $bytes_written = $howmuch;
                                $bytes_written -= $tmp_stats{"$server bytes_written"};
                                $tmp_stats{"$server bytes_written"} = $howmuch;
                                $bytes_written /= 1024*1024;
				$total_bytes_written += $bytes_written;
			}
		}
		write FILE;
	}
	my $total_hits = $total_get_missps + $total_get_hitsps;
	$total_hits++;
	my $hit_perc  = $total_get_hitsps/$total_hits*100;
	my $miss_perc = $total_get_missps/$total_hits*100;
	$hit_perc    		=~ s/(\d*\.)(\d{0,2}).*/$1$2/;
	$miss_perc   		=~ s/(\d*\.)(\d{0,2}).*/$1$2/;
	$total_bytes 		=~ s/(\d*\.)(\d{0,2}).*/$1$2/;
	$total_bytes_read	=~ s/(\d*\.)(\d{0,2}).*/$1$2/;
	$total_bytes_written	=~ s/(\d*\.)(\d{0,2}).*/$1$2/;
	
	$total_limit_maxbytes = 1 unless $total_limit_maxbytes;
	my $total_bytes_perc = $total_bytes/$total_limit_maxbytes*100;
	$total_bytes_perc =~ s/(\d*\.)(\d{0,3}).*/$1$2/;
	$elapsed_time = tv_interval ($start_time);
	$elapsed_time *= 1_000_000;
	$elapsed_time = 1_000_000 - $elapsed_time;
	$elapsed_time = 1_000_000 if $elapsed_time =~ /^-/;
	usleep $elapsed_time;



	my $ws = 0;
	my $total_str .= "     totals";
	$ws = 34 - length($total_str) - length($total_conns);
	$total_str .= " "x$ws . $total_conns;
	$ws = 42 - length($total_str) - length($total_get_hitsps);
	$total_str .= " "x$ws . $total_get_hitsps;
	$ws = 49 - length($total_str) - length($total_get_missps);
	$total_str .= " "x$ws . $total_get_missps;
	$ws = 58 - length($total_str) - length($total_limit_maxbytes);
	$total_str .= " "x$ws . $total_limit_maxbytes;
	$ws = 67 - length($total_str) - length($total_bytes);
	$total_str .= " "x$ws . $total_bytes;
	$ws = 74 - length($total_str) - length($total_bytes_perc);
	$total_str .= " "x$ws . $total_bytes_perc;
	$ws = 84 - length($total_str) - length($total_items_cached);
	$total_str .= " "x$ws . $total_items_cached;
	$ws = 92 - length($total_str) - length($total_items_change);
	$total_str .= " "x$ws . $total_items_change;
	
	$ws = 99 - length($total_str) - length($total_bytes_read);

	$total_str .= " "x$ws . $total_bytes_read;

	$ws = 109 - length($total_str) - length($total_bytes_written);	
	$total_str .= " "x$ws . $total_bytes_written;
	
	$ws = 117 - length($total_str) - 1;
	$total_str .= " "x$ws . "-";
	$ws = 125 - length($total_str) - 1;
	$total_str .= " "x$ws . "-";
	$ws = 134 - length($total_str) - 1;
	$total_str .= " "x$ws . "-";
	addstr($cnt, 5, "=====================================================================================================================================");

	init_pair(5,6,0);
        
	attron(COLOR_PAIR(5));
	addstr(++$cnt, 0, "$total_str");
        attroff(COLOR_PAIR(5));

	$total_str = '';
	$ws = 42 - length("$hit_perc%");
	$total_str .= " "x$ws . "$hit_perc%";	
	$ws = 49 - length("$miss_perc%") - length($total_str);
	$total_str .= " "x$ws . "$miss_perc%";

	attron(COLOR_PAIR(5));
	addstr(++$cnt, 0, "$total_str");
	attroff(COLOR_PAIR(5));

	addstr(++$cnt, 5, "   ");
	my $total_time = tv_interval ($start_time);
	addstr(++$cnt, 5, "** 1 second was : $total_time          ");
	addstr(++$cnt, 4, " ");
	refresh();
}
format FILE = 
@<<<<<<<<<<<<<<<<<<<<< @>>>>>> @>>>>> @>>>>>   @>>>>> @####.## @##.##@#########  @>>>>> @##.##    @##.##     @>>>  @>>>>>     @>>>>>
$server, $curr_connections, $get_hitsps, $get_missesps, $limit_maxbytes, $bytes, $usage_percentage, $curr_items, $curr_items_change, $bytes_read, $bytes_written, $threads, $uptime, $version
.

__END__




