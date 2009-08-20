# media_bundler/management/commands/bundle_media.py

"""
A Django management command to bundle our media.

This command should be integrated into any build or deploy process used with
the project.
"""

from django.core.management.base import NoArgsCommand

from optparse import make_option 

from media_bundler.conf import bundler_settings
from media_bundler import bundler
from media_bundler import versioning


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--purge', '-p', dest='purge', default=False, 
            action='store_true',
            help='Purge prior version if versioning is enabled',),
    )
    help = "Bundles site media as specified in settings.py."
    
    requires_model_validation = False
    
    def handle_noargs(self, **options):
        purge = options.get('purge')
        
        version_file = bundler_settings.BUNDLE_VERSION_FILE
        if version_file:
            vers_str = bundler_settings.BUNDLE_VERSIONER
            versioner = versioning.VERSIONERS[vers_str](purge=purge)
        else:
            versioner = None
        # We do the image bundles first because they generate CSS that may get
        # bundled by a CssBundle.
        def key(bundle):
            return -int(isinstance(bundle, bundler.PngSpriteBundle))
        bundles = sorted(bundler.get_bundles().itervalues(), key=key)
        for bundle in bundles:
            bundle.make_bundle(versioner)
        if versioner:
            versioning.write_versions(versioner.versions)
