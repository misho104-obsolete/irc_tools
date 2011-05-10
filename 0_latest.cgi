#!/usr/bin/perl

## LOG VIEWER BY SHO IWAMOTO.

## For historical reason, this file is named 0_latest.cgi.


our $THISFILENAME = "0_latest.cgi";
our $LOGDIR       = "0_raw_0/all/";

if( $ENV{'REQUEST_METHOD'} ne "POST" ) {
  my $channel = $ENV{'QUERY_STRING'};

  my $flag = 1;

  my $filename = $LOGDIR . dotted_datetime(time()) . ".txt";
  if(-f $filename && length($channel) < 40){
    my @log = log_grep($filename, $channel);
    default_html($channel, "", 1);
    print "<pre>";
    print @log;
    print "</pre></body></html>";
  }else{
    default_html($g,"");
  }
  exit 0;
}else{
  my %f = form_read();
  if($f{dt} !~ /^\d/) { default_html("Invalid Date"); exit 0; }
  my $filename = $LOGDIR . dotted_datetime(time()-$f{dt}*86400) . ".txt";
  unless(-f $filename){ default_html("","File Not Found."); exit 0; }

  my $channel = $f{ch};
  if(length($channel)>40){ default_html($channel,"Invalid Channel?"); exit 0; }

  if($channel eq ''){
    print "Location: $filename\n\n";
  }else{
    my @log = log_grep($filename, $channel);
    default_html($channel, "", 1);
    print "<pre>";
    print @log;
    print "</pre></body></html>";
  }
}
exit 0;

sub default_html{
  my $channel = shift;
  my $message = shift;
  my $connect = shift;

  if(length($channel)>40){ $channel = ""; }
  if($message) { $message = "<p>$message</p>";}
  print <<_EOF_;
Content-type: text/html

<html>
<body>
$message
<form action="$THISFILENAME" method="post">
<p><select name="dt"><option value="0">Today</option><option value="1">Yesterday</option><option value="2">2 days ago</option></select></p>
<p>Channel: <input name="ch" value="$channel"></p>
<p><input type="submit" value="go"></p>
</form>
_EOF_
  if($connect){ print "<hr>"; } else { print "</body></html>"; exit 0;}
}


sub form_read{
	my($a,$m,$n,%f);
	exit 1 if $ENV{'CONTENT_LENGTH'} > 51200;
	read(STDIN,$a,$ENV{'CONTENT_LENGTH'});
	$a =~ tr/+/ /;
	foreach (split(/[&;]/,$a)){
		($m,$n)=split(/=/,$_);
		$n =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$n =~ s/\r\n?/\n/mg;
		$f{$m} = $n;
	}
	return %f;
}

sub dotted_datetime{
    my $t = shift;
    my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime($t);
    if(length(++$mon)==1) {$mon = "0$mon";}
    if(length($mday)==1) {$mday = "0$mday";}
    $year += 1900;
    return "$year.$mon.$mday";
}

sub log_grep{
  my $filename = shift;
  my $channel = shift;

  $channel =~ s/^\#//;
  my @log;
  open(IN, $filename);
  foreach(<IN>){
   if($_ =~ /^[\d:]+ <\#$channel:/i){ push(@log, $_); }
  }
  close(IN);
  if(@log == 0){ push(@log, "No Conversation Found.\n"); }
  return @log;
}

