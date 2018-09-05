#!/usr/bin/env python

from ansible import errors
import boto3


try:
    # ansible-2.0
    from ansible.plugins.lookup import LookupBase
except ImportError:
    # ansible-1.9.x
    class LookupBase(object):
        def __init__(self, basedir=None, runner=None, **kwargs):
            self.runner = runner
            self.basedir = self.runner.basedir

            def get_basedir(self, variables):
                return self.basedir


class LookupModule(LookupBase):
    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, args, inject=None, **kwargs):
        try:
            return(boto3.client('sts').
                   get_caller_identity()['Arn'].
                   split(':')[4])

        except Exception as e:
            raise errors.AnsibleError("%s" % (e))