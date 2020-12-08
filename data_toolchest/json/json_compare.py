## compare_json_outputs.py
"""
## OVERVIEW ##
Tool to compare two json outputs, with methods to generate report log output text string or retrieve flat dictionary of old/new values

## USAGE ##
$ python compare_json_outputs.py <full path to original .json file> <full path to new .json file> <full path to output .log file> <fraction difference defining significance>

tool requires four inputs:
    original JSON file path
    new JSON file path
    path and log filename for comparison analysis output
    float value difference significance threshold (default is 10% original value)

tool generates a single output:
    log file

## FEATURE SPECIFICATIONS ##
Tool shall compare the contents of the input new JSON file to the contents of the original JSON file.
    tag:value pairs in the two input json files shall be compared according to the following criteria:
    1. tags
      1.1 identify JSON tags not consistent between the two input files.
      1.2 identify persistent JSON tags existing between the two inputs.
    2. values
      2.1 values will be evaluated for value type, with the following possible:
        (string, integer, array (list), number (float), object (dictionary), boolean, None)
        2.1.1 for tags that persist, determine if value type is changed in new json.
        2.1.2 for string, integer, and number values, determine if values can be converted to float:
            2.1.2.1 If so:
              2.1.2.1.1 determine difference
              2.1.2.1.2 calculate significance threshold from original value and input threshold fraction
              2.1.2.1.3 determine if absolute value of difference exceeds significance threshold
            2.1.2.2 If not, determine if string values equivalent
        2.1.3 for container value types:
          2.1.3.1 the tool shall expand on any nested value of list or dictionary types.
          2.1.3.2 number of elements in these value types will be part of tag comparison criteria.
          2.1.3.3 the tool shall evaluate nested tag: value pairs in the containers according to the rules above
          2.1.3.4 list expansions process the elements in order
    3. evaluation categories
      3.1 possible categories to characterize each tag:value comparison are:
            same - tag:value exactly maintained
            dropped - tag:value are not maintained in new JSON
            new - tag:value are not in original JSON
            changed - numerical value of tag somewhat different
    4. output log shall report on all categories.
      4.1 Each row shall record the tag-name, original value, original value type, new value, new value type, and comparison result message
##
"""

__version__ = 20170217

import os, sys
import json
from types import *
from datetime import datetime
# type dictionary to convert python types to json schema type names
type_dict = {StringType:'string',UnicodeType:'string',IntType:'integer',ListType:'array',
             BooleanType:'boolean',#False:'boolean',
             FloatType:'number',DictionaryType:'object',
             NoneType:None}
container_dict = {'object':'{...}','array':'[...]'}

def test_string_to_float(input_string):
    """
    Test if string type value can be converted to float for difference calculations
    :param input_string: <str> - string to be converted
    :return out_val: <float or False> - return float value, or False if conversion fails
    """
    out_val = False
    if type_dict[type(input_string)] in ['string','number','integer']:
        try:
            out_val = float(input_string)
        except:
            pass
    return out_val

def test_value_diff(old_val,new_val):
    """
    General test between two values.
    Identifies numerical difference between inputs if float, int, or string representation of former two.
    If inputs are strings that do not convert to float, directly compares.
    All else return False
    :param old_val: <float,int,str> -old value to compare against new value
    :param new_val: <float,int,str> -new value to compare against old value
    :return: diff_val: <float or boolean> - float if numerical difference found; True if strings exactly match; False for all else
    :return out_flg,diff_val: <boolean>,<float or boolean> - out_flg signifies if values could be compared,
                                                             diff_val is float value for successful numerical compares
                                                             , or boolean for text compare results
    """
    old_val_type  = type_dict[type(old_val)]
    new_val_type  = type_dict[type(new_val)]
    old_val_float = test_string_to_float(old_val)
    new_val_float = test_string_to_float(new_val)
    out_flg = False
    diff_val = False
    if old_val_float is not False and new_val_float is not False:
        diff_val = old_val_float-new_val_float
        out_flg = True
    elif old_val_type == 'string'and new_val_type == 'string':
        out_flg = True
        if old_val == new_val:
            diff_val = True
    return out_flg,diff_val

class Json_Dict_Compare_obj:
    """compares key:value pairs in two json dicts"""
    def __init__(self,key_tag='',old_keyval=False,new_keyval=False,sig_diff_frac=0.10):
        """
        generate and populate compare_dict that captures tag:value comparisons
        :param key_tag: <str> - json dictionary tag name.  Default for top level is empty string.
        :param old_keyval: <any type> - json dictionary tag:value set as standard.  If str, treats as json filepath.
        :param new_keyval: <any type> - json dictionary tag:value compared to standard.  If str, treats as json filepath.
        :param sig_diff_pct: <float> - fraction of difference calulated between input values considered to be significant
        """
        self.original_json_path = ''
        self.new_json_path      = ''
        self.compare_dict       = {'dropped':[],'new':[],'changed':[],'same':[]}
        self.key_tag            = key_tag
        self.sig_diff_frac      = sig_diff_frac

        if type(old_keyval) is str and os.path.exists(old_keyval):
            self.original_json_path = old_keyval
            old_keyval = {'':self._parse_json(self.original_json_path)}
        if type(old_keyval) is dict:
            self.old_val      = old_keyval[key_tag]
            self.old_val_type = type_dict[type(self.old_val)]
        else:
            self.old_val,self.old_val_type = '-','-'

        if type(new_keyval) is str and os.path.exists(new_keyval):
            self.new_json_path = new_keyval
            new_keyval = {'':self._parse_json(self.new_json_path)}
        if type(new_keyval) is dict:
            self.new_val      = new_keyval[self.key_tag]
            self.new_val_type = type_dict[type(self.new_val)]
        else:
            self.new_val,self.new_val_type = '-','-'

        self.val_results = {'key_tag':key_tag,
                            'old_val':self.old_val,'old_val_type':self.old_val_type,
                            'new_val':self.new_val,'new_val_type':self.new_val_type,
                            'diff':'N/A'}
        if self.old_val_type in container_dict:
            self.val_results['old_val'] = container_dict[self.old_val_type]
        if self.new_val_type in container_dict:
            self.val_results['new_val'] = container_dict[self.new_val_type]
        self.container_cnt = sum([[self.old_val_type,self.new_val_type].count(type_tag) \
                                  for type_tag in ['object','array']])
        self.diff_msg_lt = []
        self.result_tag  = 'same'
        if old_keyval is False or new_keyval is False:
            if old_keyval is False:
                self.diff_msg_lt.append('Key_tag not in original input file')
                self.result_tag = 'new'
            elif new_keyval is False:
                self.diff_msg_lt.append('Key-Tag not in new input file')
                self.result_tag = 'dropped'
            if self.container_cnt > 0: self.container_drilldown()
        elif self.old_val_type != self.new_val_type:
            self.diff_msg_lt.append('ValueType changed from %s to %s'%(self.old_val_type,self.new_val_type))
            self.result_tag = 'changed'
            if self.container_cnt > 0: self.container_drilldown()
        else:
            self.diff_msg_lt.append('ValueType %s unchanged'%(self.old_val_type))
            if self.container_cnt > 0: self.container_drilldown()
        if self.container_cnt == 0:
            compare_flg,diff_val = test_value_diff(self.old_val,self.new_val)
            if compare_flg is True and False not in [old_keyval,new_keyval]:
                if diff_val is True and [self.old_val_type,self.new_val_type].count('string') == 2:
                    self.diff_msg_lt.append('StringValue unchanged')
                elif diff_val is False:
                    self.diff_msg_lt.append('StringValue changed (%s - %s)'%(self.old_val,self.new_val))
                    self.result_tag = 'changed'
                if test_string_to_float(self.old_val) is not False:
                    old_val_sig_diff = abs(test_string_to_float(self.old_val)*sig_diff_frac)
                    if abs(diff_val) <= old_val_sig_diff:
                        self.diff_msg_lt.append('Value numerical difference of %s (not significant)'%diff_val)
                    else:
                        self.diff_msg_lt.append('Value numerical difference of %s (significant)'%diff_val)
                        self.result_tag = 'changed'
            elif compare_flg is False:
                self.diff_msg_lt.append('Cannot compare values')
            self.val_results['diff'] = ';'.join(self.diff_msg_lt)
            self.compare_dict[self.result_tag].append(self.val_results)
        # else:
        #     self.container_drilldown()

    def container_drilldown(self):
        if 'object' in [self.old_val_type,self.new_val_type]:
            old_val_keys,new_val_keys = [],[]
            if self.old_val_type == 'object': old_val_keys = sorted(self.old_val.keys())
            if self.new_val_type == 'object': new_val_keys = sorted(self.new_val.keys())
            if self.result_tag not in ['new','dropped']:
                if len(old_val_keys) != len(new_val_keys) or old_val_keys != new_val_keys or self.old_val_type != self.new_val_type:
                    self.result_tag = 'changed'
                    if len(old_val_keys) != len(new_val_keys):
                        self.diff_msg_lt.append('ObjectType number of keys changed from %d to %d'%(len(old_val_keys),len(new_val_keys)))
                    elif old_val_keys != new_val_keys:
                        self.diff_msg_lt.append('ObjectType set of keys changed')
                else:
                    self.diff_msg_lt.append('ObjectType length and keys appear unchanged (contents evaluated separately)')
            self.val_results['diff'] = ';'.join(self.diff_msg_lt)
            if self.key_tag: self.compare_dict[self.result_tag].append(self.val_results)
            combined_keys = sorted(set(old_val_keys+new_val_keys))
            for k in combined_keys:
                sub_key = k
                if self.key_tag: sub_key = '%s:%s'%(self.key_tag,k)
                sub_old_val, sub_new_val = False,False
                if self.old_val_type=='object' and k in self.old_val: sub_old_val = {sub_key:self.old_val[k]}
                if self.new_val_type=='object' and k in self.new_val: sub_new_val = {sub_key:self.new_val[k]}
                sub_compare_obj = Json_Dict_Compare_obj(sub_key,sub_old_val,sub_new_val,self.sig_diff_frac)
                for compare_key,sub_lt in sub_compare_obj.compare_dict.items():
                    for x in sub_lt:
                        self.compare_dict[compare_key].append(x)
        if 'array' in [self.old_val_type,self.new_val_type]:
            old_lt_len,new_lt_len = 0,0
            if self.old_val_type == 'array': old_lt_len = len(self.old_val)
            if self.new_val_type == 'array': new_lt_len = len(self.new_val)
            if self.result_tag not in ['new','dropped']:
                if old_lt_len != new_lt_len or self.old_val_type != self.new_val_type:
                    self.result_tag = 'changed'
                    self.diff_msg_lt.append('ArrayType number of elements changed from %d to %d'%(old_lt_len,new_lt_len))
                else:
                    self.diff_msg_lt.append('ArrayType element count appears unchanged (contents evaluated separately)')
            self.val_results['diff'] = ';'.join(self.diff_msg_lt)
            self.compare_dict[self.result_tag].append(self.val_results)
            for cnt in range(max(old_lt_len,new_lt_len)):
                sub_key = 'array elem %d'%cnt
                if self.key_tag: sub_key = '%s:(array elem-%d)'%(self.key_tag,cnt)
                sub_old_val, sub_new_val = False,False
                if cnt < old_lt_len: sub_old_val = {sub_key:self.old_val[cnt]}
                if cnt < new_lt_len: sub_new_val = {sub_key:self.new_val[cnt]}
                sub_compare_obj = Json_Dict_Compare_obj(sub_key,sub_old_val,sub_new_val,self.sig_diff_frac)
                for compare_key,sub_lt in sub_compare_obj.compare_dict.items():
                    for x in sub_lt:
                        self.compare_dict[compare_key].append(x)


    def construct_old_new_vals_flatdict(self,include_key_lt=[],filter_key_lt=[],
                                        include_new=True,
                                        include_dropped=False):
        compare_dict_tags = ['changed','same']
        if include_new: compare_dict_tags.append('new')
        if include_dropped: compare_dict_tags.append('dropped')
        metric_key_vals_dict = {}
        for compare_dict_tag in compare_dict_tags:
            results_lt = self.compare_dict[compare_dict_tag]
            for result_obj in results_lt:
                key_tag = result_obj['key_tag']
                filter_key_cnt = [filter_key in result_obj['key_tag'] for filter_key in filter_key_lt].count(True)
                if filter_key_cnt >= 1: continue
                else:
                    if include_key_lt != []:
                        if [include_key in result_obj['key_tag'] for include_key in include_key_lt].count(True) < 1:
                            continue
                        else: pass
                    result_vals_dict = {'OLD':result_obj['old_val'],'NEW':result_obj['new_val']}
                    metric_key_vals_dict[key_tag] = result_vals_dict
        return metric_key_vals_dict

    def generate_difference_separated_report_txt(self,include_key_lt=[],filter_key_lt=[],
                                                 subdict_keylt=['changed','same','new','dropped']):
        """
        Generate a str report of comparisons.
        :return txt_out: <str>
        """
        txtlines_out_lt = []
        txtlines_out_lt.append('- %s'%os.path.basename(__file__))
        txtlines_out_lt.append('- comparison generated on %s'%datetime.strftime(datetime.now(),'%Y%m%d-%H:%S'))
        txtlines_out_lt.append('- original: %s'%self.original_json_path)
        txtlines_out_lt.append('- new: %s'%self.new_json_path)

        result_headers = ['key_tag','old_val','old_val_type','new_val','new_val_type','diff']
        txtlines_out_lt.append('compare_result\t%s'%'\t'.join(result_headers))
        for compare_dict_tag in subdict_keylt:
            results = self.compare_dict[compare_dict_tag]
            for result_obj in results:
                filter_tag_cnt = [filter_key in result_obj['key_tag'] for filter_key in filter_key_lt].count(True)
                if filter_tag_cnt >= 1: continue
                else:
                    if include_key_lt != []:
                        if [include_key in result_obj['key_tag'] for include_key in include_key_lt].count(True) < 1:
                            continue
                        else: pass
                    txtlines_out_lt.append('%s\t%s'%(compare_dict_tag,'\t'.join([str(result_obj[header]) for header in result_headers])))
        txt_out = '\n'.join(txtlines_out_lt)
        return txt_out

    def _parse_json(self,json_fpath):
        """convenience method to parse jsons consistently elsewhere"""
        J = open(json_fpath,'rb')
        json_dict = json.load(J)
        J.close()
        return json_dict

def example_compare_json_files(original_json_path,new_json_path,out_fn,sig_diff_frac=0.1):
    """
    Compare json file contents, tag for tag, and level for level.
    :param original_json_path: <str> - full path to original json file name used as base for comparison.
    :param new_json_path: <str> - full path to new json file name, compared to original.
    :param out_fn: <str> - full path to output log containing differences.
    :param sig_diff_frac: <float> - fraction of original value that signals significant difference from new value
    """
    compare_obj = Json_Dict_Compare_obj(old_keyval=original_json_path,
                                        new_keyval=new_json_path,
                                        sig_diff_frac=sig_diff_frac)

    O = open(out_fn,'wb')
    compare_report_txt = compare_obj.generate_difference_separated_report_txt()
    O.write(compare_report_txt)
    O.close()

    O = open(out_fn+'.oldnew_flat.tsv','wb')
    oldnewdict = compare_obj.construct_old_new_vals_flatdict()
    sorted_dict_keys = sorted(oldnewdict.keys())
    old_json_fn = os.path.basename(original_json_path)
    new_json_fn = os.path.basename(new_json_path)
    O.write('old_json_filename\tnew_json_filename\t%s\n'%('\t'.join(['%s_OLD\t%s_NEW'%(header_metric,header_metric) \
                                         for header_metric in sorted_dict_keys])))
    O.write('%s\t%s\t%s\n'%(old_json_fn,new_json_fn,
                            '\t'.join(['%s\t%s'%(oldnewdict[h]['OLD'],oldnewdict[h]['NEW'])\
                                       for h in sorted_dict_keys])))
    O.close()



if __name__=='__main__':
    if len(sys.argv) not in [4,5]:
        print __doc__
        raise IOError
    else:
        example_compare_json_files(*sys.argv[1:])

## compare_sampleresultsfiles.py

import os,sys
from parse_resultsfile import parse_resultsfile_to_dict
from datetime import datetime

def compare_sampleresults(original_results,new_results,out_dir=None,sid_header='SAMPLE_ID',delimiter='\t'):
    """
    Method to compare result files generated by different analyses of the same source data set.
    A difference is calculated and reported for numerical results.
    Boolean values are reported for comparison of string values (original values are reported).
    :param original_results: <str> - full path to original results file. Header and sid values from this file are used for comparisons.
    :param new_results: <str> - full path to new results file.
    :param out_dir: <str> - full path to directory to deposit comparison results.
    :param sid_header: <str> - results file header tag to identify sid column.
    :param delimiter: <str> - delimiter character used to parse result files.
    :return <date>_resultscompare.tsv: <file> - Output file with same format as original_tsv
    """
    __version__ = 20160102
    if not out_dir: out_dir = os.path.dirname(new_results)

    ori_rdict = parse_resultsfile_to_dict(original_results,
                                          delimiter=delimiter,
                                          key_col_header=sid_header)
    new_rdict = parse_resultsfile_to_dict(new_results,
                                          delimiter=delimiter,
                                          key_col_header=sid_header)

    sids_to_eval = sorted(ori_rdict.keys())
    if not sids_to_eval:
        print '<WARNING> no SIDs found in original results file'
        raise IOError
    cols_to_eval = sorted(ori_rdict[sids_to_eval[0]].keys())
    if not cols_to_eval:
        print '<WARNING> no results found in original results file'
        raise IOError
    new_sids = sorted(new_rdict.keys())
    if not new_sids:
        print '<WARNING> no SIDs found in new results file'
        raise IOError
    new_cols = sorted(new_rdict[new_sids[0]].keys())
    if not new_cols:
        print '<WARNING> no results found in new results file'
        raise IOError

    date_tag       = datetime.now().strftime('%Y%m%d_%H%M%S')
    compare_dict   = {}
    compare_logtxt = []
    for sid in sids_to_eval:
        if sid not in new_sids:
            compare_logtxt.append('<WARNING> sample %s results not found in new results file'%sid)
            compare_dict[sid] = dict(zip(cols_to_eval,['NA' for x in cols_to_eval]))
            continue
        else:
            cols_dict = {}
            ori_sampdict = ori_rdict[sid]
            new_sampdict = new_rdict[sid]
            for col_name in cols_to_eval:
                try :
                    newcol_name = 'GCBIN_%d'%int(col_name)
                except:
                    newcol_name = col_name

                if newcol_name not in new_cols:
                    compare_logtxt.append('<WARNING> value %s missing from new results file for sample %s'%(col_name,sid))
                    cols_dict[col_name] = 'NA'
                    continue
                else:
                    ori_value = ori_sampdict[col_name]
                    new_value = new_sampdict[newcol_name]
                    # print col_name,newcol_name,ori_value,new_value
                    if not ori_value[0].isalpha() and not new_value[0].isalpha() and '-' not in ori_value:
                        try:
                            if '.' in ori_value or '.' in new_value: compare_value = float(ori_value)-float(new_value)
                            else:                compare_value = int(ori_value)-int(new_value)
                            if compare_value != 0:
                                compare_logtxt.append('%s-%s value differs by %s'%(sid,col_name,str(compare_value)))
                        except:
                            if ori_value == new_value: compare_txt = 'TRUE'
                            else:
                                compare_txt = 'FALSE'
                                compare_logtxt.append('%s-%s text values differ (%s-%s)'%(sid,col_name,ori_value,new_value))
                            compare_value = compare_txt+'(%s-%s)'%(ori_value,new_value)

                    else:
                        if ori_value == new_value: compare_txt = 'TRUE'
                        else:
                            compare_txt = 'FALSE'
                            compare_logtxt.append('%s-%s text values differ (%s-%s)'%(sid,col_name,ori_value,new_value))
                        compare_value = compare_txt+'(%s-%s)'%(ori_value,new_value)
                    cols_dict[col_name] = compare_value
            compare_dict[sid] = cols_dict

    out_fn = os.path.join(out_dir,'%s_compared_results.tsv'%date_tag)
    O = open(out_fn,'wb')
    O.write('# Output from compare_sampleresultsfiles.py, v. %d\n'%__version__)
    O.write('# original_results: %s\n# new_results: %s\n'%(original_results,new_results))
    O.write('%s\t%s\n'%(sid_header,'\t'.join(cols_to_eval)))
    for sid in sids_to_eval:
        O.write('%s\t%s\n'%(sid,'\t'.join([str(compare_dict[sid][col_name]) for col_name in cols_to_eval])))
    O.close()

    log_fn = os.path.join(out_dir,'%s_compared_log.txt'%date_tag)
    L = open(log_fn,'wb')
    L.write('# Output from compare_sampleresultsfiles.py, v. %d\n'%__version__)
    L.write('# original_results: %s\n# new_results: %s\n'%(original_results,new_results))
    L.write('# explicit differences noted below\n')
    [L.write('%s\n'%l) for l in compare_logtxt]
    L.close()



if __name__ == '__main__':
    compare_sampleresults(*sys.argv[1:])





