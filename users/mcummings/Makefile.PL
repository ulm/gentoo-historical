use 5.006001;
use ExtUtils::MakeMaker;
# See lib/ExtUtils/MakeMaker.pm for details of how to influence
# the contents of the Makefile that is written.
WriteMakefile(
    'NAME'		=> 'WWW::Bugzilla',
    'VERSION_FROM'	=> 'Bugzilla.pm', # finds $VERSION
    'PREREQ_PM'		=> {Carp => 0, 'File::Spec' => 0.82, WWW::Mechanize => 0.40, Class::MethodMaker => 1.08}, # e.g., Module::Name => 1.1
);
