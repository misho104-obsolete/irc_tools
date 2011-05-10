#!/usr/bin/perl

## LOG VIEWER BY SHO IWAMOTO.

## For historical reason, this file is named 0_latest.cgi.
use MIME::Base64::URLSafe;
use Encode;
use Encode::Guess qw/ euc-jp shiftjis 7bit-jis /;

our $THISFILENAME = "0_latest.cgi";
our $LOGDIR       = "0_raw_0/all/";

my ($channel, $date, $time);
if( $ENV{'REQUEST_METHOD'} eq "POST" ) {
  my %f = form_read();
  $date    = $f{dt};  # log date
  $time    = $f{tm};  # log truncation
  $channel = form_decode($f{ch}); # channel name to pick up
}else{
  $channel = form_decode_get($ENV{'QUERY_STRING'});
}

if(($date ||= 0) !~ /^\d$/){ error("Invalid Date."); }
if(($time ||= 0) !~ /^\d$/){ error("Invalid Time."); }
if(length($channel) > 40)  { error("Invalid Channel."); }
$filename = $LOGDIR . dotted_datetime(time()-$date*86400) . ".txt";
unless(-f $filename){ error("File Not Found."); }

if($ENV{'REQUEST_METHOD'} eq 'POST' && $channel eq '' and $time == 0){
  print "Location: $filename\n\n";
}else{
  my @log = log_grep($filename, $channel, $time);
  show_log($channel, $time, @log);
}
exit 0;

sub show_log{  my $c = shift; my $t = shift; my @l = @_; default_html($c, $t, "", @l); }
sub error{ default_html("", 0, $_[0]); }

sub default_html{
  my $channel = shift;
  my $time    = shift;
  my $message = shift;
  my @log     = @_;

  if($message) { $message = "<p>$message</p>"; }
  if(@log > 0) { unshift(@log, "<hr><pre>"); push(@log, "</pre>"); }

  my @timeselect;
  foreach(0..23){
    my $selected = ($time == $_) ? "selected=\"selected\"" : "";
    push(@timeselect, "<option $selected>$_</option>");
  }
  print <<_EOF_;
Content-type: text/html

<html><body>
$message
<form action="$THISFILENAME" method="post">
<p><select name="dt">
  <option value="0">Today</option>
  <option value="1">Yesterday</option>
  <option value="2">2 days ago</option>
</select>
  after: <select name="tm">@timeselect</select>
</p>
<p>
  Channel: <input name="ch" value="$channel"> 
</p>
<p><input type="submit" value="go"></p>
</form>
@log
</body></html>
_EOF_
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
sub form_decode_get{
  my $c = shift;
  $c =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  return form_decode($c);
}
sub form_decode{
  my $c = shift;
  if($c =~ /^___(.*)$/){
    return urlsafe_b64decode($1);
  }else{
    my $guess = Encode::Guess::guess_encoding($c);
    if(ref $guess){
      $c = $guess->decode($c);
      $c = Encode::encode("utf-8", $c);
    }
    return $c;
  } 
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
  my $channel  = shift;
  my $time     = shift;

  $channel =~ s/^\#//;
  my @log;
  open(IN, $filename);
  foreach(<IN>){
    if($_ =~ /^(\d\d):\d\d:\d\d [><]\#$channel:/i){
      push(@log, $_) unless $1 < $time;
    }
  }
  close(IN);
  if(@log == 0){ push(@log, "No Conversation Found.\n"); }
  return @log;
}
__END__
