import numpy as np
import pandas as pd
import os
import sys
import itertools
import re

'''
DEPRICATED VERSION

def applyRegexsToDirOfXML(directoryPath,stringPhraseList,fieldsSelect):
    """
    Applies a regex search to the list of inputTexts and a dictionary wherein the keys are a tuple of the string phrase and the file name and the values are booleans indicating whether the string phrase was found in the file.

    NOTE: case sensitive is depricated.

    Parameters
    ----------
    directoryPath : string
        A string corresponding to the path to the directory containing the xml files to be searched.
    stringPhraseList : list of strings
        A list of strings corresponding to the phrases one is interested in assessing the occurrences of.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.

    Returns
    -------
    tupleDict : dict
        A dictionary with tuples as keys and booleans as values, indicating whether the targetField was found in the inputStructs.

    """
    import os
    fileList=os.listdir(directoryPath)
    # filter the list down to only the xml files
    fileList=[iFile for iFile in fileList if iFile[-4:]=='.xml']

    # create an empty dictionary with the tuples of the string phrase and the file name as the keys
    tupleDict={}
    # iterate across pairings of the string phrases and the file names in order to create the dictionary keys
    for iStringPhrase in stringPhraseList:
        for iFile in fileList:
            tupleDict[(iStringPhrase,iFile.replace('.xml',''))]=False

    # iterate across the stringPhraseList and apply the regex search to each file
    for iStringPhrase in stringPhraseList:
        # temporary debut print statement
        print('Searching for the string phrase: '+iStringPhrase)
        # get the list of files in the directory
        # no we already got that, so we don't need to keep redoing that
        # fileList=os.listdir(directoryPath)
        # iterate across the files
        for iFile in fileList:
            # apply the regex search to the file and place it in the appropriate tuple dictionary entry
            tupleDict[(iStringPhrase,iFile.replace('.xml',''))]=applyRegexToXMLFile(os.path.join(directoryPath,iFile),iStringPhrase,fieldsSelect)

    return tupleDict
'''
def applyRegexsToDirOfXML(directoryPathORDictionary,stringPhraseList,fieldsSelect,daskify=False,savePath='',stopwords=None,lemmatizer=None):
    """
    Applies a regex search to the list of inputTexts and a dictionary wherein the keys are a tuple of the string phrase and the file name and the values are booleans indicating whether the string phrase was found in the file.

    NOTE: case sensitive is depricated.

    Parameters
    ----------
    directoryPathORDictionary : string or dictionary
        A string corresponding to the path to the directory containing the xml files to be searched.  Alternatively, a dictionary can be passed in, wherein the keys are the file names and the values are the xml dictionaries.    stringPhraseList : list of strings
        A list of strings corresponding to the phrases one is interested in assessing the occurrences of.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
    daskify : boolean, optional
        A boolean indicating whether the function should be run in parallel using the dask library.  The default is False.
    savePath : string, optional
        A string corresponding to the path to the directory where the results should be saved.  The default is '', which will save the results in the current directory.
    stopwords : list of strings, optional
        A list of strings corresponding to the words to be removed from the input text.  The default is None, which will apply the nltk default stopword list.  stopwords='' will result in no stopwords being applied.
    lemmatizer : nltk lemmatizer object, optional
        An nltk lemmatizer object to be used for lemmatization.  The default is None, which will use the nltk WordNetLemmatizer.
            
    Returns
    -------
    regexResultDF : pandas dataframe
        A pandas dataframe with two columns: 'term' and 'itemID'.  The 'term' column contains the string phrase and the 'itemID' column contains the file name.  The values are booleans indicating whether the string phrase was found in the file.
        
    """
    import os
    import pandas as pd
    import sys
    import psutil
    import re
    import numpy as np
    import datetime
    import xmltodict
    import time
    from glob import glob


    """
    Memory check for the forthcoming dataframe
    
    Actually this is all unnecessary, because boolean dataframes are super small

    # create the output dataframe
    # before doing that, compute how much memory is available
    # get the number of bytes in a gigabyte
    bytesInGB=1024**3
    # get the number of bytes in the system memory available using psutil
    systemMemoryBytes=psutil.virtual_memory().available
    # compute the number of gigabytes in the system memory
    systemMemoryGB=systemMemoryBytes/bytesInGB
    # compute the number of gigabytes to use for the output dataframe
    # the output dataframe will be a boolean dataframe that is N rows by M columns, where N is the number of string phrases and M is the number of files
    # the number of string phrases is the length of the stringPhraseList
    numStringPhrases=len(stringPhraseList)
    # the number of files is the length of the fileList
    numFiles=len(fileList)
    # the number of bytes in the output dataframe is the number of string phrases times the number of files times the number of bytes in a python boolean, which we will obtain emperically by using a 4x4 boolean dataframe
    # create a 4x4 boolean dataframe
    testDF=pandas.DataFrame([[True,False,False,False],[False,True,False,False],[False,False,True,False],[False,False,False,True]])
    # get the number of bytes in the dataframe
    bytesInDF=testDF.memory_usage(index=True,deep=True).sum()
    # compute the per item memory usage of the dataframe
    bytesPerItem=bytesInDF/16
    # use this to extrapolate the number of bytes in the forthcoming dataframe
    bytesInOutputDF=bytesPerItem*numStringPhrases*numFiles
    # compute the number of gigabytes in the output dataframe
    outputDFGB=bytesInOutputDF/bytesInGB
    # compute how this compares to the available memory
    if outputDFGB>systemMemoryGB:
        # if the expected output dataframe is larger than the available memory, then raise an error
        # TODO: implement this using a conditional switch to a sparse array in the relevant case
        raise ValueError('The expected output dataframe is larger than the available memory.  Please reduce the number of string phrases or the number of files.  Or implement this using a sparse array.')
    # if the expected output dataframe is smaller than the available memory, then go ahead and create it, but also print the expected size
    else:
        print('Output dataframe is expected to be '+str(outputDFGB)+' GB, which is less than the available '+str(systemMemoryGB)+' GB of system memory.  Proceeding with creation of output dataframe.')
    # create the output dataframe, which is a boolean dataframe with N rows and M columns, where N is the number of string phrases and M is the number of files
    # the row index will be the string phrases, and the column index will be the file names (without the file extension)
    regexResultDF=pandas.DataFrame(index=stringPhraseList,columns=[iFile.replace('.xml','') for iFile in fileList],dtype=bool)
    """
    

    """
    Preperation of the regex search phrases
    """
    # first we need to lemmaize the stringPhraseList, as the content they are being compared to will also be lemmaized
    # we will be using prepareTextForNLP(inputText,stopwordsList=None,lemmatizer=None) for this, using list comprehension
    NLPreadyStringPhraseList=[prepareTextForNLP(iStringPhrase,stopwordsList=stopwords,lemmatizer=lemmatizer) for iStringPhrase in stringPhraseList] 
    # now we compile the regexes, using list comprehension
    # we should actually do this better, and should be compiling the regex search strings such that the terms/phrases are abutted by word boundaries
    # this will prevent partial word matches
    compiledRegexes=[re.compile('\\b'+iStringPhrase+'\\b') for iStringPhrase in NLPreadyStringPhraseList]

    # NSF = ~ 4 gb and NIH = ~ 8 gb so let's just get greedy and load everything into memory


    # check if the daskify flag is set to true
    if daskify:
        # if so, then import the dask library
        import dask
        from dask.distributed import Client
        import dask.dataframe as ddf
        # TODO: implement a function that computes the appropriate dask worker / client configuration based on available system resources (e.g. cpus, threads, memory, and task type)
        # compute the number of cpus available
        numCPUs=psutil.cpu_count(logical=False)
        # compute the number of threads available
        numThreads=psutil.cpu_count(logical=True)
        # compute the number of threads per cpu
        numThreadsPerCPU=numThreads/numCPUs
        # here we'll arbitrarily set the number of CPUs to leave available to the system to 2
        reservedCPUs=2
        # compute the number of CPUs to use for the dask client
        numCPUsToUse=numCPUs-reservedCPUs
        # compute the number of threads to use for the dask client
        numThreadsToUse=numThreads-(reservedCPUs*numThreadsPerCPU)
        # given that our task is non-numeric, and is heavily regex based, we want to be a bit more conservative
        # based upon this stack overflow post: https://stackoverflow.com/questions/49406987/how-do-we-choose-nthreads-and-nprocs-per-worker-in-dask-distributed
        # we note the following advice: "...if you are spending most of your compute time manipulating Pure Python objects like strings or dictionaries then you may want to avoid GIL issues by having more processes with fewer threads each"
        # we'll use the remaining numThreadsToUse with an arbitrary number of threads per worker, which we will set to 2 (as a test)
        numThreadsPerWorker=2
        # compute the number of workers, remember to floor round
        numWorkers=int(numThreadsToUse/numThreadsPerWorker)
        # now we can create the dask client
        client=Client(n_workers=numWorkers,threads_per_worker=numThreadsPerWorker)
        print ('Created dask client with '+str(numWorkers)+' workers and '+str(numThreadsPerWorker)+' threads per worker.')
        # and also create a progress bar
        from dask.diagnostics import ProgressBar
        # create the progress bar
        pbar=ProgressBar()
        # register the progress bar with the client
        pbar.register()
        # now convert the regexResultDF to a dask dataframe
        # regexResultDF=ddf.from_pandas(regexResultDF,npartitions=numWorkers)
        # instead of this, just create a np array of the appropriate size

        """
        Loading the input (potentially)
        """
        # check if it's a dictionary, if so, you don't need to do anything
        if isinstance(directoryPathORDictionary,dict):
            # unpack the dictionary using list comprehension
            xmlDictBag=[directoryPathORDictionary[iKey] for iKey in directoryPathORDictionary.keys()]
            # also create a list of the recordIDs from the file names, there shouldn't be file extensions in the dictionary
            recordIDList=list(directoryPathORDictionary.keys())
        # check if the input is a string or a list of strings
        elif isinstance(directoryPathORDictionary,str):
            fileList=os.listdir(directoryPathORDictionary)
            # filter the list down to only the xml files using glob
            fileList=glob(os.path.join(directoryPathORDictionary,'*.xml'))
            

                      # lets use dask to do a parallelized load of the xml files in to memory
            print('Loading XML files into memory using dask...')
            # create a list of the file paths
            filePathList=[os.path.join(directoryPathORDictionary,iFile) for iFile in fileList]
            # create a dask bag from the file path list
            filePathBag=dask.bag.from_sequence(filePathList)
            # use the bag to load the xml files into memory
            def attemptXMLLoad(filePath):
                try:
                    with open(filePath,'r') as f:
                        return xmltodict.parse(f.read())
                except:
                    return filePath
            xmlDictBag=filePathBag.map(attemptXMLLoad)
            # now compute the xmlDictBag
            xmlDictBag=xmlDictBag.compute()                                  
            # print progress
            print('Loaded XML files into memory using dask.')
            print('memory usage: '+str(psutil.virtual_memory().percent)+'%')
            # also create a list of the recordIDs from the file names, but remove the file extension
            recordIDList=[iFile.replace('.xml','') for iFile in fileList]
        # otherwise if it's a list of strings
        elif isinstance(directoryPathORDictionary,list) and all([isinstance(iFile,str) for iFile in directoryPathORDictionary]):
            filePathList=directoryPathORDictionary

            # lets use dask to do a parallelized load of the xml files in to memory
            print('Loading XML files into memory using dask...')
            # create a list of the file paths
            # create a dask bag from the file path list
            filePathBag=dask.bag.from_sequence(filePathList)
            # use the bag to load the xml files into memory
            def attemptXMLLoad(filePath):
                try:
                    with open(filePath,'r') as f:
                        return xmltodict.parse(f.read())
                except:
                    return filePath
            xmlDictBag=filePathBag.map(attemptXMLLoad)
            # now compute the xmlDictBag
            xmlDictBag=xmlDictBag.compute()                                  
            # print progress
            print('Loaded XML files into memory using dask.')
            print('memory usage: '+str(psutil.virtual_memory().percent)+'%')
            # also create a list of the recordIDs from the full file paths, be sure you're only getiting the file name and that the extension is removed

            # otherwise, check if the input is a dictionary, and if so, just use it, but also unpack it as the first key is just the file name

        # in either case create an ouput array with columns for the records, and rows for the keywords / regex results
        # first we need to compute the number of records
        numRecords=len(xmlDictBag)
        # now we can create the output array
        outputArray=np.zeros((len(stringPhraseList),numRecords),dtype=bool)


        '''
        Here is a description of the forthcoming task that we would like to parallelize:
        For each XML file found in the directory, we will load it into a dictionary using the xmltodict library.
        Then we will index into the field that the regex search is to be applied to using fieldsSelect in order to get the text content.
        Then we will use applyRegexesToText(inputText,compiledRegexes) to apply the regex searches (one for each item in stringPhraseList).
        For each file, the relevant text field of which has been extracted with fieldsSelect, we will get a boolean vector of N items long (where N is the number of items in stringPhraseList) from applyRegexesToText.
        Note that, although all of these operations are modifying the data in regexResultDF, they are all modifing independent portions of the data frame, 
        becaues each file-wise operation is modifying a different column of the dataframe, and so it is this column-wise parallelism that we will exploit.
        '''
        # the file names (and also column names) are found in the fileList variable
        # thus we'll use a dask iterator to iterate across the dask dataframe columns
        # we'll use the dask delayed decorator to create a function that will apply the regex search to a single column of the dataframe
        """
        def applyRegexesToColumn(columnName):
            # get the file name
            # apparently they are already coming in from fileList with the .xml extension removed
            # get the file path
            filePath=os.path.join(directoryPath,columnName)
            # use applyRegexesToFieldFromXMLFile(xmlFilePath,regexList,fieldsSelect) to apply the regex search to the file
            # this returns a boolean vector of length N, where N is the number of items in stringPhraseList
            regexResultVec=applyRegexesToFieldFromXMLFile(filePath,compiledRegexes,fieldsSelect)
            # return the regexResultVec
            return regexResultVec

        # now create another wrapper that applies this to a list of file names
        def applyRegexesToColumnList(columnNameList):
            # initialize the regexResultVec as a list of blank lists
            regexResultVec=[[] for i in range(len(columnNameList))]
            # iterate across the column names
            for iColumnNameIndex,iColumnName in enumerate(columnNameList):
                # apply applyRegexesToColumn and catch the result
                regexResultVec[iColumnNameIndex]=applyRegexesToColumn(iColumnName)
            # return the regexResultVec
            return regexResultVec
        """
        def applyRegexesToXMLDictionaries(xmlDictBag):
            # initialize the regexResultVec as a list of blank lists
            regexResultVec=[[] for i in range(len(xmlDictBag))]
            # iterate across the column names
            for iFileIndex,iFile in enumerate(xmlDictBag):
                # apply applyRegexesToColumn and catch the result
                regexResultVec[iFileIndex]=applyRegexesToFieldFromXMLFile(iFile,compiledRegexes,fieldsSelect)
            # return the regexResultVec
            return regexResultVec

        # now we can use the dask iterator to iterate across the columns of the dask dataframe
        # the output of this will be a list of dask delayed objects, which we can then compute and place in the appropriate column of the dataframe
        # iterate across the columns
        # for iFile in fileList:
        # apply the regex search to all of the elements of the file name list using dask delayed and a lambda function that has the applyRegexesToColumn function as its body
        regexResultBag=dask.delayed(applyRegexesToXMLDictionaries)(xmlDictBag)
        # now we can compute the regexResultBag
        regexResultBag=regexResultBag.compute()
        # debug print
        # print type
        print(str(type(regexResultBag)))
        # print shape
        print(str(regexResultBag.shape))
        # take the results of the regexResultBag and place them in the appropriate column of the regexResultDF
        for iFileIndex,iFile in enumerate(fileList):
            # get the regex result vector
            regexResultVec=regexResultBag[iFileIndex]
            # place the regex result vector in the appropriate column of the regexResultDF
            outputArray[:,iFileIndex]=regexResultVec

        # create a pandas dataframe from the output array, the column names should be the record IDs from recordIDList, while the row names should be the string phrases from stringPhraseList
        regexResultDF=pd.DataFrame(outputArray,index=stringPhraseList,columns=recordIDList,dtype=bool)


        # now we can convert the regexResultDF back to a pandas dataframe
        # the above should have already produced a pandas dataframe, so the next line is unnecessary
        # regexResultDF=regexResultDF.compute()
        # also close the dask client and deregister the progress bar
        client.close()
        pbar.unregister()
        pbar.close()
    # if the daskify flag is not set to true, then we'll just iterate across the files and apply the regex search to each file
    else:
        print('Daskify flag is set to False.  Subsequent regex application may take a while for ' + str(len(directoryPathORDictionary)) + ' files.')
        
        # check if the input is a directory path or a dictionary, and load the content accordingly
        if isinstance(directoryPathORDictionary,str):
            fileList=os.listdir(directoryPathORDictionary)
            # filter the list down to only the xml files
            fileList=[iFile for iFile in fileList if iFile[-4:]=='.xml']
            # load the xml files into a dictionary using xmltodict
            for iFile in fileList:
                # get the file path
                filePath=os.path.join(directoryPathORDictionary,iFile)
                # attempt to load the file into a dictionary
                try:
                    xmlDictBag.append(xmltodict.parse(open(filePath,'rb')))
                except:
                    # append an empty dictionary if the file could not be loaded
                    xmlDictBag.append({})
            # also create a list of the recordIDs from the file names, but remove the file extension
            recordIDList=[iFile.replace('.xml','') for iFile in fileList]
            # otherwise, check if the input is a dictionary, and if so, just use it, but also unpack it as the first key is just the file name
        elif isinstance(directoryPathORDictionary,dict):
            # unpack the dictionary using list comprehension
            xmlDictBag=[directoryPathORDictionary[iKey] for iKey in directoryPathORDictionary.keys()]
            # also create a list of the recordIDs from the file names, there shouldn't be file extensions in the dictionary
            recordIDList=list(directoryPathORDictionary.keys())
        
        # create a numpy array to hold the output
        outputArray=np.zeros((len(stringPhraseList),len(xmlDictBag)),dtype=bool)
        
        # in either case, we'll need to iterate across the files and apply the regex search to each file
        # create a holder for the timing results
        timesHolder=np.zeros(len(xmlDictBag))

        # iterate across the files
        for iFileIndex,iFile in enumerate(xmlDictBag):
            # this returns a boolean vector of length N, where N is the number of items in stringPhraseList
            # start the timer
            startTime=time.time()
            regexResultVec=applyRegexesToFieldFromXMLFile(iFile,compiledRegexes,fieldsSelect)
            # stop the timer
            endTime=time.time()
            # store the time
            timesHolder[iFileIndex]=endTime-startTime
            # place the regexResultVec in the appropriate column of the dataframe
            outputArray[:,iFileIndex]=regexResultVec
        # print the average time
        print('Average time to apply regexes to a single file: ' + str(np.mean(timesHolder)) + ' seconds.')

        # create a pandas dataframe from the output array, the column names should be the record IDs from recordIDList, while the row names should be the string phrases from stringPhraseList
        regexResultDF=pd.DataFrame(outputArray,index=stringPhraseList,columns=recordIDList,dtype=bool)
    return regexResultDF
                      
def flattenDictionary(dictionaryToFlatten):
    """
    This is a helper function that flattens a nested dictionary into a single level dictionary. 
    The output keys are the concatenation of the input keys, separated by underscores.
    It can handle nested dictionaries of any depth.

    Parameters
    ----------
    dictionaryToFlatten : dict
        The dictionary to be flattened.

    Returns
    -------
    flattenedDictionary : dict
        The flattened dictionary.
    """
    # initialize the flattened dictionary
    flattenedDictionary={}
    # iterate across the keys of the dictionary
    for iKey in dictionaryToFlatten.keys():
        # check if the value is a dictionary
        if type(dictionaryToFlatten[iKey])==dict:
            # if so, then recursively call this function on the sub-dictionary
            subDictionary=flattenDictionary(dictionaryToFlatten[iKey])
            # iterate across the keys of the sub-dictionary
            for iSubKey in subDictionary.keys():
                # concatenate the keys
                # BUT lets use double underscores to separate the keys, since some of the keys already have underscores in them
                concatenatedKey=iKey+'__'+iSubKey
                # place the value in the flattened dictionary
                flattenedDictionary[concatenatedKey]=subDictionary[iSubKey]
        # otherwise, just place the value in the flattened dictionary
        else:
            # place the value in the flattened dictionary
            flattenedDictionary[iKey]=dictionaryToFlatten[iKey]
    # return the flattened dictionary
    return flattenedDictionary











# get the xml files in the directory using glob


def quantifyDataCompleteness(inputData,fieldSequenceToSearch=None,maxDepth=3):
    """
    This is a data quality assesment function which computes the number of empty / null values for each field in a given data set.
    It returns a pandas dataframe with two columns:  the first column is the field name and the second column is the number of empty / null values for that field.
    In addition to having a row for each field in the data structure, it also has a row that reflects the total number of records assesed, which is functionally the 
    maximum potential value for any field (e.g. in the case of a field that is empty for all records).

    Parameters
    ----------
    inputData : either a pandas dataframe, list of strings, or a dictionary of dictionaries (in which each sub-dictionary is an xml dictionary)
        The data structure to be assessed for completeness.  If a pandas dataframe, then the fieldSequenceToSearch will be treated as the column name.  If a list of strings, then they are assumed to be xml formatted files and treated as such.  
        If a dictionary of dictionaries, then the fieldSequenceToSearch is treated as the field sequence necessary to obtain the information *on a per entry basis* 
        (in other words, it is assumed that the top level of the dictionary structure constitutes a structure wherein each key is the record identifier (e.g. file name minus the extension), and each associated value of these is the direct output of loading that file with xmltodict).    
    fieldSequenceToSearch : list of strings, optional
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field within which completeness will be assessed.  Will throw an error if not specified correctly.  The default is None, which will assume that the first field is of the dictionary is the root tag.
    maxDepth : int, optional
        The maximum depth within the (presumably nested) dictionary structure to search for the content to be assessed for completeness.  
        The default is 3, which is assessed *AFTER* the fieldSequenceToSearch is applied.  
        This means, that if the root tag is provided, it will still search to depth 3, but if it is not, it will only search to depth three.
        NOTE: this is done by assessing underscores in the names of the fields, so if the field names already have underscores in them, this will mess up (unless we can somehow find a robust way around this)
    
    Returns
    -------
    dataCompletenessDF : pandas dataframe
        A pandas dataframe with two columns:  the first column is the field name and the second column is the number of empty / null values for that field.
        The last row is the total number of records assessed.

    """
    import os
    import pandas as pd
    import json
    import xmltodict
    import numpy as np
    from warnings import warn
    import json
    
    # go ahead and create the output dataframe, which will have two columns:  the first column is the field name and the second column is the number of empty / null values for that field.
    dataCompletenessDF=pd.DataFrame(columns=['fieldName','numEmpty'])

    # first, determine if the input is a pandas dataframe or a list of file paths
    # we'll handle the pandas dataframe case first because that is the easier case
    if isinstance(inputData,pd.DataFrame):
        # if it's a pandas dataframe, create the output dataframe, which will have two columns:  the first column is the field name and the second column is the number of empty / null values for that field.
       
        # iterate across the columns in the input dataframe
        for iCol in inputData.columns:
            # determine the number of empty values in the column using the isempty function
            numEmpty=inputData[iCol].apply(isempty).sum()
            # add a row to the output dataframe
            dataCompletenessDF=dataCompletenessDF.append({'fieldName':iCol,'numEmpty':numEmpty},ignore_index=True)
        # add a row for the total number of records
        dataCompletenessDF=dataCompletenessDF.append({'fieldName':'totalNumRecords','numEmpty':inputData.shape[0]},ignore_index=True)
    
    # now we'll handle the case where the input is a list of file paths or a dictionary of dictionaries
    elif (isinstance(inputData,list) and all([isinstance(iFile,str) for iFile in inputData])) or (isinstance(inputData,dict) and all([isinstance(iFile,dict) for iFile in inputData.values()])):
        # in either case we'll be outputting to a pandas dataframe, BUT we don't know what the 
        # so go ahead and create the output dataframe, with nothing in it and no columns
        dataCompletenessDF=pd.DataFrame()
        # also, as an intermediary holder, create a blank list with N elements, where N is the number of files
        # this will be used to hold the intermediary data completeness dictionaries
        dataCompletenessDictList=[{} for iFile in inputData]
        # in either case we'll be iterating across the elements of the list or dictionary
        # detect which case we have
        if isinstance(inputData,list):
            # check if it is a list of file paths
            # just check the first element
            if os.path.isfile(inputData[0]):
                case='listOfFilePaths'
            # otherwise, check if it is a list of xml dictionaries
            elif isinstance(inputData[0],dict):
                case='listOfXmlDicts'
            # otherwise, throw an error
            else:
                raise ValueError('The inputData is a list, but it is not a list of file paths or a list of xml dictionaries.')
        elif isinstance(inputData,dict):
            # check if it is a dictionary of dictionaries
            # just check the first element
            if isinstance(inputData[list(inputData.keys())[0]],dict):
                case='dictOfXmlDicts'
            # otherwise, throw an error
            else:
                raise ValueError('The inputData is a dictionary, but it is not a dictionary of xml dictionaries.')
        # now that we know the case, we can iterate across the elements of the list or dictionary
        # print the case
        print('The inputData is a '+case + ' case.')
        # parse them into a usable format, which will be a list of dictionaries
        # create a list to hold the parsed dictionaries
        parsedDictList=[ {} for iFile in inputData]
        if case=='listOfFilePaths':
            for iFileIndex,iFile in enumerate(inputData):
                # lets try it with a try / except block
                if isinstance(iFile,str) and os.path.splitext(iFile)[1]=='.xml':
                    try:
                        # load the file
                        parsedDictList[iFileIndex]=xmltodict.parse(open(iRecord,'r').read())
                    except:
                        parsedDictList[iFileIndex]={}
                        warn('Could not load file '+iRecord)
            # otherwise if it is a json file, then we'll load it with json
                elif isinstance(iRecord,str) and os.path.splitext(iRecord)[1]=='.json':
                    # lets try it with a try / except block
                    try:
                        # load the file
                        parsedDictList[iFileIndex]=json.load(open(iRecord,'r'))
                    except:
                        parsedDictList[iFileIndex]={}
                        warn('Could not load file '+iRecord)
        elif case=='listOfXmlDicts':
            # do nothing, because it is already a list of xml dictionaries
            parsedDictList=inputData
        elif case=='dictOfXmlDicts':
            # convert it to a list of xml dictionaries
            parsedDictList=list(inputData.values())
        
        # now we'll iterate across the elements of the list of dictionaries
        for iRecordIndex,iRecord in enumerate(parsedDictList):
            # now we'll iterate across the fields in the record
            # first, index into the entry using the specified field sequence and extractValueFromDictField
            if not fieldSequenceToSearch == None:
                # index into the entry using the specified field sequence and extractValueFromDictField
                try:
                    iRecord=extractValueFromDictField(iRecord,fieldSequenceToSearch)
                except:
                    # if it doesn't work set it to a blank dictionary
                    iRecord={}
            else:
                # do nothing
                pass
            # now flatten the dictionary
            iRecord=flattenDictionary(iRecord)
            # create a holder dictionary to hold the key : bool pairs that
            # (1) survive the maxDepth check (those that do not are not included in the output dictionary or final dataframe)
            # (2) are not empty as determined by the isempty function
            holderDict={}
            # now iterate across the fields in the record
            for iField in iRecord.keys():
                # check if the name has N-1 or more DOUBLE underscores, where N is the maxDepth.  If it does, we are not including it.
                if not iField.count('__') >= maxDepth-1:
                    # if it doesn't, then we'll check if it is empty
                    if isempty(iRecord[iField]):
                        # if it is empty, we will add a true value to the holderDict for this key value
                        holderDict[iField]=True
                    else:
                        # if it is not empty, we will add a false value to the holderDict for this key value
                        holderDict[iField]=False
                else:
                    # if it does, we will not include it in the holderDict
                    pass
            # now that we've iterated across the fields in the record, we'll add the holderDict to the dataCompletenessDictList
            dataCompletenessDictList[iRecordIndex]=holderDict
        # now that we have the intermediary list, we can concatenate it into a dataframe, but first we need to convert each dictionary into a dataframe, with the keys being columns and the values being rows
        # use a list comprehension to do this
        #boolRecordDFList=[pd.DataFrame.from_dict(iDict,orient='index') for iDict in dataCompletenessDictList]
        boolRecordDF = pd.DataFrame()
        boolRecordDF = boolRecordDF.append(dataCompletenessDictList,ignore_index=True,sort=False)

        # in the event that any files were completely inacessible, and thus the holder dictionary remains an empty dictionary, we need to count these separately, as they will simply be omitted during the concatenation step above
        # just use list comprehension to determine how many dictionaries have no keys
        numInaccessibleFiles=len([iDict for iDict in dataCompletenessDictList if len(iDict.keys())==0])
        # now we just need to get a count of the True values for each field, as these indicate empty fields
        # first, get the column names
        colNamesVec=boolRecordDF.columns
        # then, iterate across the columns
        numEmptyVec=[boolRecordDF[iCol].sum() for iCol in colNamesVec]
        # create a dataframe from the numEmptyVec and colNamesVec
        dataCompletenessDF=pd.DataFrame({'fieldName':colNamesVec,'numEmpty':numEmptyVec})
        # add a row for the total number of records
        dataCompletenessDF=pd.concat([dataCompletenessDF,pd.DataFrame({'fieldName':'totalNumRecords','numEmpty':len(parsedDictList)},index=[0])],ignore_index=True)
        # add a row for the total number of inaccessible files
        dataCompletenessDF=pd.concat([dataCompletenessDF,pd.DataFrame({'fieldName':'totalNumInaccessibleFiles','numEmpty':numInaccessibleFiles},index=[0])],ignore_index=True)
    return dataCompletenessDF






def isempty(inputContent):
    '''
    This function determines whether the input is null, empty, '', zero, or NaN, or equivalent.
    Is this ugly?  Yes it is. 

    NOTE: Technically this is a duplicate of the same named function in the processData function set,
    but is included here in order to avoid cross-module dependencies.  At least for now.

    Inputs:
        inputContent: any
            Any input content.
    Outputs:    
        isEmpty: boolean
            A boolean indicating whether the input is null, empty, '', zero, or NaN, or equivalent.
    '''
    import numpy as np
    try:
        # if the input is null, return True
        if inputContent is None:
            return True
        else:
            raise Exception
    except:
        try:
            # if the input is empty, return True
            if inputContent=='':
                return True
            else:
                raise Exception
        except:
            try:
                # if the input is empty, return True
                if inputContent.lower().replace('.','')=='nan':
                    return True
                else:
                    raise Exception
            except:
                try:
                    # if the input is zero, return True
                    if inputContent==0:
                        return True
                    else:
                        raise Exception
                except:
                    try:
                        # if the input is NaN, return True
                        if np.isnan(inputContent):
                            return True
                        else:
                            raise Exception
                    except:
                        # otherwise, return False
                        return False

def convertTupleDictToEfficientDict(tupleDict,rowDescription='',colDescription=''):
    """
    Convets a dictionary with tuples as keys to a dictionary with three keys: rowNames, colNames, and dataMatrix.  
    The rowName and colName are themselves dictionaries, with two fields:  "nameValues" and "description".  
    "nameValues" is a list of the unique names of the rows or columns, respectively.  "description" is a string describing the data in the row or column.
    The dataMatrix is a N by M matrix of reflecting the values associated with the tuples.

    This is done because presumably this is a more efficient way to store the data.
    
    Parameters
    ----------
    tupleDict : dict
        A dictionary with tuples as keys and booleans as values, indicating whether the targetField was found in the inputStructs.
    rowDescription : string, optional
        A string describing the data in the rows. The default is '', a blank string.
    colDescription : string, optional  
        A string describing the data in the columns. The default is '', a blank string.

    Returns
    -------
    efficientDict : dict
        A more efficient dictionary with the following fields:
        - rowName: string, the names of the rows (the unique values of the targetField)
        - colName: string, the names of the columns (the identifiers of the inputStructs)
        - rowDescription: string, a description of the rows
        - colDescription: string, a description of the columns
        - dataMatrix: len(rowName) by len(colName) matrix of booleans indicating whether the targetField was found in the inputStructs

    """
    import numpy as np
    # get the row and column names
    rowName=[iTuple[0] for iTuple in tupleDict.keys()]
    colName=[iTuple[1] for iTuple in tupleDict.keys()]
    # get the unique row and column names and preserve the order
    uniqueRowName=list(dict.fromkeys(rowName))
    uniqueColName=list(dict.fromkeys(colName))
    # create the efficient dictionary
    efficientDict={}
    efficientDict['rowName']={}
    efficientDict['colName']={}
    efficientDict['dataMatrix']=np.zeros((len(uniqueRowName),len(uniqueColName)))
    # go ahead and create the description field for the row and column names
    efficientDict['rowDescription']=rowDescription
    efficientDict['colDescription']=colDescription
    # before iterating across the rows and colums, go ahead and fill in the row and column names
    efficientDict['rowName']=uniqueRowName
    efficientDict['colName']=uniqueColName
    # iterate across the rows and columns and fill in the data matrix

    for iRow in range(len(uniqueRowName)):
        for iCol in range(len(uniqueColName)):
            # get the row and column names
            iRowName=uniqueRowName[iRow]
            iColName=uniqueColName[iCol]
            # get the value
            iValue=tupleDict[(iRowName,iColName)]
            # fill in the data matrix
            efficientDict['dataMatrix'][iRow,iCol]=iValue
    return efficientDict

def regexSearchAndSave(directoryPath,stringPhraseList,fieldsSelect,daskify=False,savePath=''):
    """
    EFFICIENTLY applies regex searches to the specied field (from fieldsSelect) of each xml file in directoryPath.
    Optionally daskifys this operation if daskify=True.
    Saves down the results either as a pandas dataframe csv or as an hdf5 file.

    Parameters
    ----------
    directoryPath : string
        A string corresponding to the path to the directory containing the xml files to be searched.
    stringPhraseList : list of strings
        A list of strings corresponding to the phrases one is interested in assessing the occurrences of.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
    daskify : boolean, optional
        A boolean indicating whether to use dask to parallelize the regex search.  The default is False.
    savePath : string, optional
        A string corresponding to the path to the directory where the results should be saved.  The default is '', which will save the results in the current directory.

    Returns
    -------
    None.

    """
    import os
    import pandas
    import h5py

    # apply the regex search to the contents using applyRegexsToDirOfXML
    outDataframe=applyRegexsToDirOfXML(directoryPath,stringPhraseList,fieldsSelect,daskify=daskify)

    # determine whether to save the results as a csv or as an hdf5 file
    # if the savePath is empty, then save the results as a csv in the current directory
    if savePath=='':
        print('saving as csv to '+os.getcwd())
        # create the save file name
        saveFileName='regexSearchResults.csv'
        # create the save path
        savePath=os.path.join(os.getcwd(),saveFileName)
        # save the file
        outDataframe.to_csv(savePath)
    # if the extension of the savePath is .csv, then save the results as a csv
    elif os.path.splitext(savePath)[1]=='.csv':
        print('saving as csv to '+savePath)
        # save the file
        outDataframe.to_csv(savePath)
    # if the extension of the savePath is .hdf5, then save the results as an hdf5 file
    # but also be sure to save the column and row names as separate datasets, as they will not fit as attributes
    elif os.path.splitext(savePath)[1]=='.hdf5' or os.path.splitext(savePath)[1]=='.h5' or os.path.splitext(savePath)[1]=='.hdf' or os.path.splitext(savePath)[1]=='.hd5' :
        print('saving as hdf5 to '+savePath)
        # save the file
        outDataframe.to_hdf(savePath,key='dataMatrix',mode='w')
        # save the column and row names as datasets
        # with h5py.File(savePath,'a') as f:
        #    f.create_dataset('rowName',data=outDataframe.index.values)
        #    f.create_dataset('colName',data=outDataframe.columns.values)
        # close the file
        # f.close()
    # otherwise do nothing
    else:
        pass
    return

def pdDataFrameFromHF5obj(hf5obj):
    """
    Creates a pandas dataframe from an hdf5 object.  The presumption is that .to_hdf was used to save the dataframe.
    As a result, the object (when indexed with the relevant key) has the following subkeys:
    KeysViewHDF5 ['axis0', 'axis1', 'block0_items', 'block0_values']
    
    Parameters
    ----------
    hf5obj : hdf5 object
        An hdf5 object that has been indexed with the relevant key.

    Returns
    -------
    outDataframe : pandas dataframe
        A pandas dataframe created from the hdf5 object.

    """
    import pandas as pd
    # get the keys
    keys=hf5obj.keys()
    # get the row and column names, and convert them from bytes to strings
    rowName=[i.decode('utf-8') for i in hf5obj['axis1']]
    colName=[i.decode('utf-8') for i in hf5obj['axis0']]
    # get the data
    data=hf5obj['block0_values']
    # create the dataframe
    outDataframe=pd.DataFrame(data=data,index=rowName,columns=colName)
    return outDataframe





'''
def regexSearchAndSave(directoryPath,stringPhraseList,fieldsSelect,savePath=''):
    """
    Applies a regex search to the field specified by the list in fieldsSelect (single field; sequence represents nested fields) to the xml files in the directory specified by directoryPath.
    Saves the results in an efficient, compressed hdf5 file.

    DEPRICATION NOTE: this version of regexSearchAndSave has been depricated.  There's too much cruft in it now.

    NOTE: case sensitive is depricated.

    Parameters
    ----------
    directoryPath : string
        A string corresponding to the path to the directory containing the xml files to be searched.
    stringPhraseList : list of strings
        A list of strings corresponding to the phrases one is interested in assessing the occurrences of.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
      savePath : string, optional
        A string corresponding to the path to the directory where the results should be saved.  The default is '', which will save the results in the current directory.
    
    Returns 
    -------

    The output is saved down as an hdf5 file.
   
    """
    import os
    import h5py
    import xmltodict
    # TODO: make this more robust relative to alternative ways of inputting the items to be searched, see tupleDictFromDictFields for example inference behavior.
    # TODO: consider implementing inference behavior for the fieldsSelect, using the first xml file in the directory to infer the fieldsSelect.

    # apply the regex search to the contents using applyRegexsToDirOfXML
    tupleDict=applyRegexsToDirOfXML(directoryPath,stringPhraseList,fieldsSelect)
    # convert the tupleDict to an efficientDict
    efficientDict=convertTupleDictToEfficientDict(tupleDict)
    # try and infer the data source from the first xml file in directoryPath
    try: 
        # start by getting the contents of the directory
        fileList=os.listdir(directoryPath)
        # get the first xml file
        firstXMLFile=[iFile for iFile in fileList if iFile.endswith('.xml')][0]
        # load the object
        with open(os.path.join(directoryPath,firstXMLFile)) as fd:
            firstXMLObject=xmltodict.parse(fd.read())
            #close the file
        fd.close()
        # get the data source using detectDataSourceFromSchema
        dataSource=detectDataSourceFromSchema(firstXMLObject)
        # use this metadata to set the metadata for the efficientDict
        if dataSource=='NSF':
            efficientDict['rowDescription']='Searched Keywords'
            efficientDict['colDescription']='NSF Award Number'
        elif dataSource=='NIH':
            efficientDict['rowDescription']='Searched Keywords'
            efficientDict['colDescription']='NIH Application Number'
        elif dataSource=='grantsGov':
            efficientDict['rowDescription']='Searched Keywords'
            efficientDict['colDescription']='Grants.Gov Opportunity ID'
        else:
            efficientDict['rowDescription']='Searched Keywords'
            efficientDict['colDescription']='Presumptive grant identifier'
    except:
        # if this fails, just set the metadata to be generic
        efficientDict['rowDescription']='Searched Keywords'
        efficientDict['colDescription']='Presumptive grant identifier'
    # set the data and attribute keys for the hdf5 file
    # apparently rowName and colName are too big to save as attributes, so they have to be saved as datasets
    dataKeys=['dataMatrix','rowName','colName']
    attributeKeys=['rowDescription','colDescription']

    # save the efficientDict as an hdf5 file
    if savePath=='':
        savePath=os.getcwd()
    # create the save file name
        saveFileName='regexSearchResults_'+fieldsSelect[-1]+'.hdf5'
        # create the save path
        savePath=os.path.join(savePath,saveFileName)
    # otherwise use the provided savePath
    else:
        savePath=savePath
        # but make sure the directory that would contain the file exists
        if not os.path.exists(os.path.dirname(savePath)):
            os.makedirs(os.path.dirname(savePath))
    # save the file
    with h5py.File(savePath,'w') as f:
        # iterate across the data keys and save the data
        for iKey in dataKeys:
            f.create_dataset(iKey,data=efficientDict[iKey],compression='gzip')
        # iterate across the attribute keys and save the attributes
        for iKey in attributeKeys:
            f.attrs[iKey]=efficientDict[iKey]
    # close the file
    f.close()
    return

    '''

def fieldExtractAndSave(inputStructs,targetField,nameField=['infer'],savePath=''):
    """
    Extracts the values of the target field from the input structures and saves the results in an efficient, compressed hdf5 file.

    Parameters
    ----------
    inputStructs : list of strings, xml strings, or dictionaries
        A list of valid objects (file paths, xml strings, or dictionary objects) to be searched.
    targetField : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
    nameField : list of strings, optional
        A string corresponding to the field, presumed to be present in all input structures, to be used as the name for the input structure.  The default is 'infer', which will attempt to infer the name field from the input structures.
    savePath : string, optional
        A string corresponding to the path to the directory where the results should be saved.  The default is '', which will save the results in the current directory.
        If savePath is set to None, then the results will not be saved.
    
    Returns 
    -------

    resultsDF : pandas dataframe
        A pandas dataframe containing the results of the field extraction.
   
    """
    import os
    import h5py
    import xmltodict
    import pandas as pd

    # go ahead and parse the nameField logic
    # if nameField is a singular list, with a single entry of 'infer', then set the infer flag to true
    if nameField==['infer']:
        inferNameField=True
    else: 
        inferNameField=False

    # start by determining what the first element of the inputStructs is
    firstElement=inputStructs[0]
    if isinstance(firstElement,str):
    # if it's a file path then test if it's a valid file path
        if os.path.isfile(firstElement):
            # if it's a valid file path then test if it's an XML file
            if firstElement.endswith('.xml'):
                # if it's an XML file then read it in as a dictionary
                inputType='xmlFile'
                # load it up and test the source 
                if inferNameField:
                    with open(firstElement) as fd:
                        firstElementObject=xmltodict.parse(fd.read())
                    fd.close()
                    # get the data source using detectDataSourceFromSchema
                    dataSource=detectDataSourceFromSchema(firstElementObject)
            else:
                # if it's not an XML file then raise an error
                raise ValueError('The inputStructs variable contains a file-like string with non-"xml" extension that is not a valid file path.')
        # if it's a string but not a file, check if it's a valid XML string
        elif firstElement.startswith('<?xml version="1.0" encoding="UTF-8"?>'):
            inputType='xmlString'
            # load it up and test the source
            if inferNameField:
                firstElementObject=xmltodict.parse(firstElement)
                # get the data source using detectDataSourceFromSchema
                dataSource=detectDataSourceFromSchema(firstElementObject)
        # TODO: maybe also consider checking if it's a valid JSON string
    # if it's not a string then check if it's a dictionary
    elif isinstance(firstElement,dict):
        inputType='dict'
        if inferNameField:
            # get the data source using detectDataSourceFromSchema
            dataSource=detectDataSourceFromSchema(firstElement)
    # if it's not a string or a dictionary then raise an error
    else:
        raise ValueError('The inputStructs variable contains an item that is not a valid file path, XML string, or dictionary.')
    print('input type '+inputType+' detected')
    # go ahead and specify name field
    if inferNameField:
        if dataSource == 'NSF':
            targetNameField=['rootTag','Award','AwardID']
        elif dataSource == 'NIH':
            targetNameField=['rootTag','APPLICATION_ID']
        elif dataSource == 'grantsGov':
            targetNameField=['rootTag','OpportunityID']
        # handle the failure case
        elif dataSource== None:
            targetNameField=''
        # set the nameField
        nameField=targetNameField

    # initalize a pandas dataframe with columns for 'itemID' and 'fieldValue' to store the results
    # ensure that it has N blank rows, where N is the number of inputStructs
    resultsDF=pd.DataFrame(columns=['itemID','fieldValue'],index=range(len(inputStructs)))
    
    # loop through the inputStructs and extract the target field
    for iIndex,iStruct in enumerate(inputStructs):
        # surround in try catch
        try: 
            # load it up as appropriate, given the inputType
            if inputType=='xmlFile':
                with open(iStruct) as fd:
                    iStructObject=xmltodict.parse(fd.read())
                fd.close()
            elif inputType=='xmlString':
                iStructObject=xmltodict.parse(iStruct)
            elif inputType=='dict':
                iStructObject=iStruct
            # extract the target field
            targetValue=extractValueFromDictField(iStructObject,targetField)
            # extract the name field
            # NOTE: come back and clean up this logic later, it is not doing what is intended at the moment.
            if not nameField=='' :
                nameValue=extractValueFromDictField(iStructObject,nameField)
            elif nameField=='' and inputType=='xmlFile' :
                # assume that you're suppoesd to get it from the name of the file, but throw an error if the input isn't a string
                if isinstance(inputStructs,str):
                    nameValue=os.path.basename(iStruct).split('.')[0]
                else:    
                    raise ValueError('The nameField variable is not "infer" but the inputStructs variable is not a string and thus the file name is unknown.  No possible way to determine name without "infer" method.')
            else:
                raise ValueError('The nameField variable is not "infer" but the inputStructs variable is not a file and thus the file name is unknown.  No possible way to determine name without "infer" method.')
            # add the results to the dataframe, but don't use append because it has been depricated
            resultsDF.loc[iIndex,'itemID']=nameValue
            resultsDF.loc[iIndex,'fieldValue']=targetValue
        except:
            # if there's an error print the error and the index
            print('unable to parse or load content of index '+str(iIndex) + '\n' +  str(inputStructs))

    # save the results
    if savePath is not None:
    # establish the subdirectories if necessary
        if not os.path.isdir(os.path.dirname(savePath)):
            os.makedirs(savePath)
        # save the results
        resultsDF.to_csv(savePath,index=False)               
    return resultsDF

def wordCountForField(inputStructs,targetField,nameField='infer',savePath=''):
    """
    Using fieldExtractAndSave, this function extracts the (presumably) text content of the target field, for each
    input structure and then performs a word count on the extracted text.  The results are returned as a pandas dataframe
    and saved down to the specified savePath if savePath is not None.

    Parameters
    ----------
    inputStructs : list of strings, xml strings, or dictionaries
        A list of valid objects (file paths, xml strings, or dictionary objects) to be searched.
    targetField : list of strings
        A list of strings corresponding to the *nested* sequence of fields to be searched.  First field is the root tag.  Last field is
        the target field.  Intermediate fields are nested tags.
    nameField : list of strings
        A list of strings corresponding to the *nested* sequence of fields to be searched.  First field is the root tag.  Last field is
        the name field.  Intermediate fields are nested tags.  If set to 'infer', then the name field is inferred from the file name.
    savePath : string
        The path to which the results should be saved.  If None, then the results are not saved.

    Returns
    -------
    resultsDF : pandas dataframe
        A pandas dataframe with two columns: 'itemID' and 'wordCount'. The 'itemID' column contains the name of the input structure, and the 'wordCount'
        column contains the word count of the target field for each input structure.
    """
    import pandas as pd
    import re
    import os
    import numpy as np

    # extract the target field
    resultsDF=fieldExtractAndSave(inputStructs,targetField,nameField=nameField,savePath=None)
    # what we should now have is a pandas dataframe with two columns: 'itemID' and 'fieldValue'
    # the field value should be a string containing the text content of the target field
    # we'll use a regex method to count the number of words

    # create a blank vector to hold the word counts
    wordCounts=np.zeros(resultsDF.shape[0])

    for iIndexes,iRows in resultsDF.iterrows():
        # get the text content for the current entry
        currentText=iRows['fieldValue']
        # if it isn't empty, then perform the word count
        if not pd.isnull(currentText):
            # perform the word count
            # alternatively: len(re.findall(re.compile('\\b[A-Za-z]+\\b'), currentText))
            wordCounts[iIndexes]=len(re.findall(r'\w+', currentText))
        # if it is empty, then set the word count to zero
        else:
            wordCounts[iIndexes]=0

    # create an output dataframe using the 'itemID' field of the input dataframe and the wordCounts vector
    resultsDF=pd.DataFrame({'itemID':resultsDF['itemID'],'wordCount':wordCounts})

    # save the results
    if savePath is not None:
    # establish the subdirectories if necessary
        if not os.path.isdir(os.path.dirname(savePath)):
            os.makedirs(savePath)
        # save the results
        resultsDF.to_csv(resultsDF,index=False)
    return resultsDF

def countsFromCoOccurrenceMatrix(coOccurrenceMatrix,rowsOrColumns='rows',axisLabels=None,savePath=''):
    """
    This function takes in a co-occurrence matrix and returns a pandas dataframe with the counts of the number of times
    each item *OCCURS IRRESPECTIVE OF COOCURRENCE WITH OTHER ITEMS*. In other words, this function sums the rows or columns
    (the matrix should be symmetric) and returns the results as a pandas dataframe.

    Parameters
    ----------
    coOccurrenceMatrix : numpy array or pandas dataframe
        A square matrix with the rows and columns corresponding to the same set of items.
        In the typical case in this package, wherein this is a term co-occurrence matrix, the rows and columns
        correspond to the instances of co-occurrence of the terms.
    rowsOrColumns : string
        Either 'rows' or 'columns', depending on whether you want the counts to be computed with respect to the rows or the columns of the input matrix.
        Probably doesn't make sense if you target the larger of the two dimensions of the input matrix.
    axisLabels : list of strings
        A list of strings corresponding to the labels of the rows or columns of the input matrix.  If None, then the labels are assumed to be integers.
    savePath : string
        The path to which the results should be saved

    Returns
    -------
    resultsDF : pandas dataframe
        A pandas dataframe with two columns: 'itemID' and 'count'. The 'itemID' column contains the label of the row or column of the input matrix, and the 'count'
        column contains the count of the number of times each item occurs in the in the input matrix. 
    
    """
    import pandas as pd
    import numpy as np
    import os
    # if the input is a pandas dataframe, then convert it to a numpy array
    if isinstance(coOccurrenceMatrix,pd.DataFrame):
        coOccurrenceMatrix=coOccurrenceMatrix.values
        # if the axis labels are not specified, then use either the row or column labels of the input matrix
        if axisLabels is None:
            if rowsOrColumns=='rows':
                axisLabels=coOccurrenceMatrix.index
            elif rowsOrColumns=='columns':
                axisLabels=coOccurrenceMatrix.columns
    # if it's a numpy array we don't need to do anything
    elif isinstance(coOccurrenceMatrix,np.ndarray):
        # if the axis labels are not specified, then use integers
        if axisLabels is None:
            axisLabels=np.arange(coOccurrenceMatrix.shape[0])
    # if it's not a numpy array or a pandas dataframe, then raise an error
    else:
        raise ValueError('Input matrix must be a numpy array or pandas dataframe')
    # sum the rows or columns of the input matrix (should be equivalent)
    if rowsOrColumns=='rows':
        results=np.sum(coOccurrenceMatrix,axis=1)
    elif rowsOrColumns=='columns':
        results=np.sum(coOccurrenceMatrix,axis=0)
    # convert the results to a pandas dataframe
    resultsDF=pd.DataFrame({'itemID':axisLabels,'count':results})
    # save the results
    if savePath is not None:
    # establish the subdirectories if necessary
        if not os.path.isdir(os.path.dirname(savePath)):
            os.makedirs(savePath)
        # save the results
        resultsDF.to_csv(savePath,index=False)
    return resultsDF


def coOccurrenceMatrix(occurenceMatrix,rowsOrColumns='rows',savePath='',rowLabels=None,colLabels=None):
    """
    This function takes in a non-square matrix and computes the co-occurrence matrix, which is a square matrix
    where each entry is the number of times an item in the row occurs with an item in the column.  The results
    are returned with respect to either the rows or the columns of the input matrix, depending on the input of 
    the rowsOrColumns variable.  

    In this way, this analysis only makes sense if you select the smaller of the two dimensions of the input matrix

    Parameters
    ----------
    occurenceMatrix : numpy array or pandas dataframe
        A non-square matrix with the rows corresponding to one set of items and the columns corresponding to another set of items.
    rowsOrColumns : string
        Either 'rows' or 'columns', depending on whether you want the co-occurrence matrix to be computed with respect to the rows or the columns of the input matrix.
        'columns' will analyze co-occurences _within_ the columns of the input matrix, and 'rows' will analyze co-occurences _within_ the rows of the input matrix.
    savePath : string
        The path to which the results should be saved.  If None, then the results are not saved.

    Returns
    -------
    coOccurrenceMatrix : numpy array of dtype int
        A square matrix with the rows and columns corresponding to the items in the rows or columns of the input matrix, depending on the rowsOrColumns variable.
        The i and j elements are understood to correspond to the same set of items, such that the i,j element is the number of times the i item occurs with the j item.
        
        In the case of a boolean matrix representing keywords along the colums and grants along the rows, a co-occurance matrix for the 
        columns would indicate how often each keyword occurs with each other keyword.  A co-occurance matrix for the rows would indicate the number
        of terms shared by each pair of grants.
        NOTE: keywords are actually the rows.
    
    """
    import numpy as np
    import pandas as pd
    import h5py
    from warnings import warn

    """
    this doesn't do what was expected / intended.  rowsums= number hits per term across documents, colsums = number of terms per document.
    Thus if rows are terms and columns are records, the dotproduct of the transpose of the matrix with the matrix will give you the number of times each term co-occurs with each other term.
    whereas the dotproduct of the matrix with the transpose of the matrix will give you the number of terms shared by each pair of records.
    
    # lets go ahead and check what the sum would be across each axis of the input matrix
 
    dimPassCheck=np.zeros(occurenceMatrix.ndim,dtype=bool)
    for iDims in range(occurenceMatrix.ndim):
        # get the sum across the current axis
        currDimSums=np.sum(occurenceMatrix,axis=iDims)
        # a count of co-occurrences only makes sense of things can co-occur along a given axis, so we'll check to see if there are any summed values of two or greater for each axis
        # if there are no sums of two or greater along this axis, then this axis isn't a valid choice for performing a co-occurrence analysis.
        dimPassCheck[iDims]=np.any(currDimSums>=2)

    # use dimPassCheck to determine if the axis requested in rowsOrColumns is valid
    # remember, requesting "rows" means that the desired output is a square matrix with N rows and columns, where N is the number of rows in the input matrix (and vice versa for "columns")
    if rowsOrColumns=='rows':
        if not dimPassCheck[0]:
            raise ValueError('The rowsOrColumns variable is set to "rows" but there are no rows with two or more values in the input matrix.  Thus, there are no co-occurrences along the specified dimension')
    elif rowsOrColumns=='columns':
        if not dimPassCheck[1]:
            raise ValueError('The rowsOrColumns variable is set to "columns" but there are no columns with two or more values in the input matrix.  Thus, there are no co-occurrences along the specified dimension')
    """
    import warnings
    # if the input is a pandas dataframe, then convert it to a numpy array
    if isinstance(occurenceMatrix,pd.DataFrame):
        currRowNames=occurenceMatrix.index
        currColNames=occurenceMatrix.columns
        occurenceMatrix=occurenceMatrix.values
        # ensure occurenceMatrix is a int matrix, so that np.dot will return a count of co-occurrences rathern than a boolean indicating whether or not there was a co-occurrence
        occurenceMatrix=occurenceMatrix.astype(int)
    # if the input is a numpy array, then proceed
    elif isinstance(occurenceMatrix,np.ndarray) and not rowLabels==None and not colLabels==None:
        # if it's not a pandas dataframe, and instead a numpy array, then you're not going to get row and column names
        # so we have to generate dummy names, which will simply be integers
        currRowNames=rowLabels
        currColNames=colLabels
        # ensure occurenceMatrix is a int matrix, so that np.dot will return a count of co-occurrences rathern than a boolean indicating whether or not there was a co-occurrence
        occurenceMatrix=occurenceMatrix.astype(int)
    elif isinstance(occurenceMatrix,np.ndarray):
        # if it's not a pandas dataframe, and instead a numpy array, then you're not going to get row and column names
        # so we have to generate dummy names, which will simply be integers
        currRowNames=np.arange(occurenceMatrix.shape[0])
        currColNames=np.arange(occurenceMatrix.shape[1])
        # ensure occurenceMatrix is a int matrix, so that np.dot will return a count of co-occurrences rathern than a boolean indicating whether or not there was a co-occurrence
        occurenceMatrix=occurenceMatrix.astype(int)
    # if the input is neither a pandas dataframe nor a numpy array, then raise an error
    else:
        raise ValueError('The input must be a pandas dataframe or a numpy array')
    # parse the case logic for rows or columns
    if rowsOrColumns=='rows':
        # compute the number of times that items co-occur

        coOccurrenceMatrix=np.dot(occurenceMatrix,occurenceMatrix.T)
        # set the row names
        rowNames=currRowNames
        # set the column names
        columnNames=currRowNames
    elif rowsOrColumns=='columns':
        # compute the co-occurrence matrix
        # coOccurrenceMatrix=np.dot(occurenceMatrix,occurenceMatrix.T)
        # is it actually
        coOccurrenceMatrix=np.dot(occurenceMatrix.T,occurenceMatrix)
        # set the row names
        rowNames=currColNames
        # set the column names
        columnNames=currColNames
    # if the rowsOrColumns variable is not set to 'rows' or 'columns', then raise an error
    else:
        raise ValueError('The rowsOrColumns variable must be set to either "rows" or "columns"')
    
    # determine the desired saving behavior
    if savePath is not None:
        # in any of the available cases when saving, it will be wortwhile to know whether the 
        # row / column labels (indexes) are simply sequential integers or not.  If they are sequential integers we can basically ignore them.
        # run a check to see if they are sequential integers
        # we'll use a try except here, because we don't know if the input rowNames is simply the output of DataFrame.index (and thus a list of strings, integers, etc.) or if it's a numpy array from np.arange
        try:
            # if it's a numpy array, then we can use the np.all function to check if it's sequential
            if np.all(np.arange(len(rowNames))==[int(x) for x in rowNames]):
                indexesMeaningful=False
            else:
                indexesMeaningful=True
        except:
            # if rowNames is made up of of strings, you'll get a `ValueError: invalid literal for int()` error
            # in this case, we'll just assume that the indexes are meaningful
            indexesMeaningful=True


        # if it's not none, then check it if is blank (''), or a specific format
        if savePath=='':
            # if it's blank, then they haven't provided a desired format, so we have to use a heuristic for this
            # we'll just set an arbitrary value here, to serve as the heuristic limit
            # in this case, what the value represents is the number of rows (or columns) that we would consider the maximum reasonable to store in a csv
            # in essence: if there are sufficiently few values, then it's fine to store the data as an uncompressed csv.
            # for example, a 1000 by 1000 matrix would be 1,000,000 numeric values which would be 8,000,000 bytes, or 8 MB for float 64 (or 4 MB for float 32)
            thresholdCSV=1000
            # also set the string for the default name
            defaultName='coOccurrenceMatrix'
            # if the number of rows or columns is less than the threshold, then save as a csv
            if coOccurrenceMatrix.shape[0]<thresholdCSV:
                # if the indexes are meaningful, then save the row and column names as well
                if indexesMeaningful:
                    # save the co-occurrence matrix as a csv
                    # make sure that it is being saved with the right column and row names, in accordance with rowsOrColumns
                    if rowsOrColumns=='rows': 
                        coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=rowNames,columns=rowNames)
                    elif rowsOrColumns=='columns':
                        coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=columnNames,columns=columnNames)
                    #coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=rowNames,columns=columnNames)
                    coOccurrenceMatrixDF.to_csv(defaultName+'.csv')
                else:
                    # save the co-occurrence matrix as a csv
                    coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=None,columns=None)
                    coOccurrenceMatrixDF.to_csv(defaultName+'.csv')
            # if the number of rows or columns is greater than the threshold, then save as an hdf5
            else:
                # if the indexes are meaningful, then save the row and column names as well
                if indexesMeaningful:
                    # save the co-occurrence matrix as an hdf5
                    with h5py.File(defaultName+'.hdf5','w') as f:
                        f.create_dataset('dataMatrix',data=coOccurrenceMatrix,compression='gzip')
                        f.create_dataset('rowName',data=rowNames,compression='gzip')
                        f.create_dataset('colName',data=columnNames,compression='gzip')
                else:
                    # save the co-occurrence matrix as an hdf5
                    with h5py.File(defaultName+'.hdf5','w') as f:
                        f.create_dataset('dataMatrix',data=coOccurrenceMatrix,compression='gzip')
                # in either case, close the file
                f.close()
        # if it's not blank, then check if it's a csv or an hdf5
        elif savePath.endswith('.csv'):
            # if it's a csv, then save the co-occurrence matrix as a csv essentially the same way as above
            if indexesMeaningful:
                # save the co-occurrence matrix as a csv
                if rowsOrColumns=='rows': 
                        coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=rowNames,columns=rowNames)
                elif rowsOrColumns=='columns':
                    coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=columnNames,columns=columnNames)
                coOccurrenceMatrixDF.to_csv(savePath)
            else:
                # save the co-occurrence matrix as a csv
                coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=None,columns=None)
                coOccurrenceMatrixDF.to_csv(savePath)
        elif savePath.endswith('.hdf5'):
            # if it's an hdf5, then save the co-occurrence matrix as an hdf5 essentially the same way as above
            if indexesMeaningful:
                # save the co-occurrence matrix as an hdf5
                with h5py.File(savePath,'w') as f:
                    f.create_dataset('dataMatrix',data=coOccurrenceMatrix,compression='gzip')
                    f.create_dataset('rowName',data=rowNames,compression='gzip')
                    f.create_dataset('colName',data=columnNames,compression='gzip')
            else:
                # save the co-occurrence matrix as an hdf5
                with h5py.File(savePath,'w') as f:
                    f.create_dataset('dataMatrix',data=coOccurrenceMatrix,compression='gzip')
            # in either case, close the file
            f.close()

        # if it's not blank, csv, or hdf5, or None then raise an error
        else:
            raise ValueError('The savePath variable must be either blank (''), None, or end with ".csv" or ".hdf5"')      

    # throw a warning if the co-occurence matrix is all zeros or boolean (as it should be a count)
    # compute this using np.unique
    uniqueValues=np.unique(coOccurrenceMatrix)
    # if the only unique values are 0 and 1 (or merely 0 or 1), then throw a warning
    # just assume if the sum of the unique values is 1 or 0 and the length is less than 3, that the warning should be thrown
    if (uniqueValues.sum()<=1) and (len(uniqueValues)<3):
        warnings.warn('The co-occurrence matrix is boolean or all zeros. This is likely an error. Please check the input data and try again.')




    # return the results
    return coOccurrenceMatrix

def convertStandardHDF5toPandas(inputHDF5obj):
    """
    In the current toolset, HDF5 files are formatted with the following standard fields:

        f.create_dataset('dataMatrix',data=coOccurrenceMatrix,compression='gzip')
        f.create_dataset('rowName',data=rowNames,compression='gzip')
        f.create_dataset('colName',data=columnNames,compression='gzip')

    Additionally, the dataMatrix, which is an np.array, is typically exceptionally sparse and (usually but not always) boolean.

    This function takes in an HDF5 file with this standard format and returns a pandas dataframe with the dataMatrix as the values and the row and column names as the indexes.
    
    Parameters
    ----------
    inputHDF5obj : hdf5 object
        An hdf5 object with the standard format described above.

    Returns
    -------
    dataMatrixDF : pandas dataframe
        A pandas dataframe with the dataMatrix as the values and the row and column names as the indexes.
    """
    import pandas as pd
    import numpy as np
    # get the column and row names, and convert them to strings.  Remember, they are stored as byte strings in the hdf5 file
    columnNames=[x.decode('utf-8') for x in inputHDF5obj['colName']]
    rowNames=[x.decode('utf-8') for x in inputHDF5obj['rowName']]
    # for now we'll assume it's boolean and that even if the data array is large we don't need to 
    # convert it to a sparse matrix
    dataMatrixDF=pd.DataFrame(inputHDF5obj['dataMatrix'],index=rowNames,columns=columnNames)
    return dataMatrixDF

def sumMergeMatrix_byCategories(matrix,categoryKeyFileDF,targetAxis='columns',savePath=''):
    """
    This function takes in a matrix and category dictionary (in the form of a two column pandas dataframe) and returns a new matrix
    where the elements of the specified axis have been condensed into the agglomerations specified by the category dictionary.
    In this way, the output matrix will retain the same number of opposite axis elements, but will have N number of `targetAxis` elements,
    where N is the number of unique categories in the category dictionary.

    Parameters
    ----------
    matrix : pandas dataframe
        A matrix of some sort, presumably bool, but potentially numeric.  The column / row indexes should correspond to the 
        identifiers (first column) in the `categoryKeyFileDF`, and be consistent with the axis requested in the `targetAxis` variable.
    categoryKeyFileDF : pandas dataframe
        A two column pandas dataframe where the first column contains the identifiers (presumably `itemID`) 
        and the second column contains the category labels (presumably `fieldValue`); presumably as in the convention of the output of fieldExtractAndSave.
    targetAxis : string
        Either 'rows' or 'columns', depending on whether you want to sum merge the rows or columns of the input matrix.  This is the axis
        across which the identifiers (from categoryKeyFileDF[`itemID`]) will be searched for.
    savePath : string
        The path to which the results should be saved.  If None, then the results are not saved.  If '', then the results are saved to the current directory.

    Returns
    -------
    sumMergeMatrix : pandas dataframe
        A pandas dataframe with summations across the specified axis for each unique category in the category dictionary.  The non-requested axis's 
        indexes should be preserved, however the requested axis's indexes should be replaced with the unique categories from the category dictionary.
    
    NOTE: consider refactoring this in light of the hd5 functionality implemented in subsetHD5DataByKeyfile
    """
    import pandas as pd
    import numpy as np
    import os
    import h5py
    import time
    # check if the input matrix is a pandas dataframe
    # if it is, then proceed
    # if it isn't then raise an error explaning why a pandas dataframe is necessary (the column / row indexes need to be matched against the category dictionary))
    if not isinstance(matrix,pd.DataFrame):
        raise ValueError('The input matrix must be a pandas dataframe in order to match category indentities from `categoryKeyFileDF` with specific records in the matrix.')
    
    # make an attempt to parse the input categoryKeyFileDF.  Start by trying to index into the columns 'itemID' and 'fieldValue'.  If that doesn't work, throw a warning and index into the first two columns, with the first being assumed to be the equivalent of 'itemID' and the second assumed to be the equivalent of 'fieldValue'.
    try:
        # as noted in the except clause here, for whatever reason .values is converting the categoryLabels to floats, so we need to convert them to strings
        recordIDs=categoryKeyFileDF['itemID'].values
        categoryLabels=categoryKeyFileDF['fieldValue'].values
    except:
        print('Warning: The input categoryKeyFileDF does not have the expected column names.  Attempting to infer the appropriate columns.  THIS MAY RESULT IN AN ERROR')
        # note it is interpreting the categoryKeyFileDF content (which are numeric IDs) as floats, so we need to convert them to integers, so we need to convert them to strings first
        recordIDs=[str(int(x)) for x in categoryKeyFileDF.iloc[:,0].values]
        categoryLabels=list(categoryKeyFileDF.iloc[:,1].values)
    # go ahead and establish the unique categories
    # ? <' not supported between instances of 'float' and 'str'
    # I don't know why I have to do this, but apparently I have to convert categoryLabels to a list of strings, even though there arent any floats in there
    categoryLabels=[str(x) for x in categoryLabels]
    uniqueCategories=np.unique(categoryLabels)

    # go ahead and use the targetAxis to obtain the appropriate axis labels
    # TODO: consider updating this to accept integer-based indexing to indicate dimension

    rowLabels=matrix.index
    columnLabels=matrix.columns
    # print the value and type of the first item of row and column labels


    # initialize a new matrix to store the results, but take in to account targetAxis
    if targetAxis=='rows':
        sumMergeMatrix=pd.DataFrame(index=uniqueCategories,columns=columnLabels)
    elif targetAxis=='columns' or targetAxis=='cols':
        sumMergeMatrix=pd.DataFrame(index=rowLabels,columns=uniqueCategories)

    # now loop through the unique categories and sum merge the appropriate rows or columns
    # give a print statement indicating where we stand in the process and the task ahead
    print('Sum merging matrix by categories.  ' + str(len(recordIDs)) + ' to be merged into ' + str(len(uniqueCategories)) + ' categories.')
    # start a timer
    # debug print categoryLabels with ten items per line
    #print('categoryLabels: ')
    #for i in range(0,len(categoryLabels)):
    #    if i%10==0:
    #        print('')
    #    print(categoryLabels[i],end=' ')
    #print('')

    startTime=time.time()
    for iCategory in uniqueCategories:
        # get the indexes of the records that match the current category
        #print('iCategory: ' + str(iCategory))
        # create a vector that identifies the indexes of the records in categoryLabels that match the current category
        currentLabelBoolVec=[x==iCategory for x in categoryLabels]
        # print the sum of the currentLabelBoolVec
        #print('sum(currentLabelBoolVec): ' + str(sum(currentLabelBoolVec)))
        # get the indexes of true values in currentLabelBoolVec using np.where
        currentCategoryIndexes=np.where(currentLabelBoolVec)[0]


        # print the currentCategoryIndexes
        # debug print statement: indicate how many records were found for the current category
        #print('Found ' + str(len(currentCategoryIndexes)) + ' records for category: ' + iCategory)
        if len(currentCategoryIndexes)==0:
            # actually, don't raise this error because it's possible that we have been passed a post-threshold input matrix in which all of the records for a given sub-organization have been removed.
            # raise ValueError('There are no records in the categoryKeyFileDF that match the current category: '+iCategory)
            # raise an error if there are no records that match the current category

            # the column for this category should already exist sumMergeMatrix, but it's possible that it's simply blank rather than set to zeros
            # so lets go ahead and set it to zeros
            if targetAxis=='rows':
                # print a warning indicating that there are no records for the current category
                print('Warning: There are no records in the categoryKeyFileDF that match the current category: '+iCategory)
                sumMergeMatrix.loc[iCategory,:]=0
            elif targetAxis=='columns' or targetAxis=='cols':
                sumMergeMatrix.loc[:,iCategory]=0
                print('Warning: There are no records in the categoryKeyFileDF that match the current category: '+iCategory)

            # print an indicator as to which category did not have any records
            print('Warning: There are no records in the categoryKeyFileDF that match the current category: '+iCategory)
        # use these indexes to subset recordIDs
        else :
            currentCategoryRecordIDs=recordIDs[currentCategoryIndexes]
            # print the length and contents of currentCategoryRecordIDs
            # use these indexes to subset the input matrix, keeping in mind the targetAxis
            
            if targetAxis=='rows':
                # index into the relevant rows of the matrix]
                currentCategoryMatrix=matrix.loc[[iRow in currentCategoryRecordIDs for iRow in matrix.index],:]
                # sum merge the current category matrix
                currentCategoryMatrix=currentCategoryMatrix.sum(axis=0)
                # print the sum and the shape of the current category matrix
                # add the results to the corresponding location in the sumMergeMatrix
                sumMergeMatrix.loc[iCategory,:]=currentCategoryMatrix
            elif targetAxis=='columns' or targetAxis=='cols':
                currentCategoryMatrix=matrix.loc[:,[iRow in currentCategoryRecordIDs for iRow in matrix.columns]]
                # sum merge the current category matrix
                currentCategoryMatrix=currentCategoryMatrix.sum(axis=1)
                # print the sum and the shape of the current category matrix
                # add the results to the corresponding location in the sumMergeMatrix
                sumMergeMatrix.loc[:,iCategory]=currentCategoryMatrix
   
    # print a message indicating that the merge process is complete
    print('Sum merge operations complete.  Time elapsed: ' + str(time.time()-startTime) + ' seconds.')
    
    
    # determine the desired saving behavior, stealing this code from coOccurrenceMatrix
    if savePath is not None:
        # we don't need to run a check here to determine if the rows and indexes are meaningful
        # they *have* to be, given the above algorithm

        # if it's not none, then check it if is blank (''), or a specific format
        if savePath=='':
            # if it's blank, then they haven't provided a desired format, so we have to use a heuristic for this
            # we'll just set an arbitrary value here, to serve as the heuristic limit
            # in this case, what the value represents is the number of rows (or columns) that we would consider the maximum reasonable to store in a csv
            # in essence: if there are sufficiently few values, then it's fine to store the data as an uncompressed csv.
            # for example, a 1000 by 1000 matrix would be 1,000,000 numeric values which would be 8,000,000 bytes, or 8 MB for float 64 (or 4 MB for float 32)
            thresholdCSV=1000
            # also set the string for the default name
            defaultName='categorySumMergeMatrix'
            # if the number of rows or columns is less than the threshold, then save as a csv
            if sumMergeMatrix.shape[0]<thresholdCSV:          
                # save the sumMergeMatrix matrix as a csv
                sumMergeMatrix.to_csv(defaultName+'.csv')
                print('Saved sumMergeMatrix matrix as a csv to \n' + defaultName+'.csv')
            # if the number of rows or columns is greater than the threshold, then save as an hdf5
            else:
                # save the co-occurrence matrix as an hdf5
                with h5py.File(defaultName+'.hdf5','w') as f:
                    f.create_dataset('dataMatrix',data=sumMergeMatrix.values,compression='gzip')
                    f.create_dataset('rowName',data=sumMergeMatrix.index,compression='gzip')
                    f.create_dataset('colName',data=sumMergeMatrix.columns,compression='gzip')
                # now close the file
                f.close()
                print('Saved sumMergeMatrix matrix as an hdf5 to \n' + defaultName+'.hdf5')
        # if it's not blank, then check if it's a csv or an hdf5
        elif savePath.endswith('.csv'):
            # if it's a csv, then save the co-occurrence matrix as a csv essentially the same way as above
            sumMergeMatrix.to_csv(savePath)
            print('Saved sumMergeMatrix matrix as a csv to \n' + savePath)

        elif savePath.endswith('.hdf5'):
            # if it's an hdf5, then save the co-occurrence matrix as an hdf5 essentially the same way as above
            with h5py.File(defaultName+'.hdf5','w') as f:
                f.create_dataset('dataMatrix',data=sumMergeMatrix.values,compression='gzip')
                f.create_dataset('rowName',data=sumMergeMatrix.index,compression='gzip')
                f.create_dataset('colName',data=sumMergeMatrix.columns,compression='gzip')
                # now close the file
                f.close()
                print( 'Saved sumMergeMatrix matrix as an hdf5 to \n' + savePath)
        # if it's not blank, csv, or hdf5, or None then raise an error
        else:
            raise ValueError('The savePath variable must be either blank (''), None, or end with ".csv" or ".hdf5"')

        # return the results
    return sumMergeMatrix      

def sumMergeMatrix_byCategories_REFACTOR(matrix,categoryKeyFileDF,targetAxis='columns',savePath=''):
    """
    This is a refactored version of the sumMergeMatrix_byCategories function.  The previous version takes an exceptional amount of time,
    and so this refactoring is an attempt to substantially improve the performance of the function.

    This function takes in a matrix and category dictionary (in the form of a two column pandas dataframe) and returns a new matrix
    where the elements of the specified axis have been condensed into the agglomerations specified by the category dictionary.
    In this way, the output matrix will retain the same number of opposite axis elements, but will have N number of `targetAxis` elements,
    where N is the number of unique categories in the category dictionary.

    Parameters
    ----------
    matrix : pandas dataframe
        A matrix of some sort, presumably bool, but potentially numeric.  The column / row indexes should correspond to the 
        identifiers (first column) in the `categoryKeyFileDF`, and be consistent with the axis requested in the `targetAxis` variable.
    categoryKeyFileDF : pandas dataframe
        A two column pandas dataframe where the first column contains the identifiers (presumably `itemID`) 
        and the second column contains the category labels (presumably `fieldValue`); presumably as in the convention of the output of fieldExtractAndSave.
    targetAxis : string
        Either 'rows' or 'columns', depending on whether you want to sum merge the rows or columns of the input matrix.  This is the axis
        across which the identifiers (from categoryKeyFileDF[`itemID`]) will be searched for.
    savePath : string
        The path to which the results should be saved.  If None, then the results are not saved.  If '', then the results are saved to the current directory.

    Returns
    -------
    sumMergeMatrix : pandas dataframe
        A pandas dataframe with summations across the specified axis for each unique category in the category dictionary.  The non-requested axis's 
        indexes should be preserved, however the requested axis's indexes should be replaced with the unique categories from the category dictionary.
    
    NOTE: consider refactoring this in light of the hd5 functionality implemented in subsetHD5DataByKeyfile
    """
    import pandas as pd
    import numpy as np
    import time
    # and checking and parsing the input variables

    # check if the input matrix is a pandas dataframe
    # if it is, then proceed
    # if it isn't then raise an error explaning why a pandas dataframe is necessary (the column / row indexes need to be matched against the category dictionary))
    if not isinstance(matrix,pd.DataFrame):
        raise ValueError('The input `inputDF` must be a pandas dataframe in order to match category indentities from `categoryKeyFile` with specific records in the matrix.')
    # go ahead and sort the input dataframe by the target axis
    # this will make it easier to extract the target records
    if targetAxis=='rows' or targetAxis==0 or targetAxis=='0':
        # sort the dataframe by the index
        inputDF=matrix.sort_index(axis=0)
    elif targetAxis=='columns' or targetAxis==1 or targetAxis=='1':
        # sort the dataframe by the columns
        inputDF=matrix.sort_index(axis=1)
    else:
        # print the current value of targetAxis
        print('The current value of `targetAxis` is: '+str(targetAxis))
        raise ValueError('The input `targetAxis` cannot be parsed.  Please enter either "rows" or "columns".')

    # parse the input category key file
    # if it's a dictionary, convert it to a pandas dataframe, as we'll be creating a boolean mask of the record ID vector / axis
    if isinstance(categoryKeyFileDF,dict):
        # convert the dictionary to a pandas dataframe
        # remember we want the record IDs to be the first column and the category labels to be the second column
        # go ahead and create an empty target dataframe
        categoryKeyFileDF_temp=pd.DataFrame(columns=['itemID','fieldValue'])
        # loop through the dictionary to create a list of record IDs and a list of the associated category label repeated for the number of record IDs for the current key
        # the value associated with the key should already be a list
        for iKeys in range(len(categoryKeyFileDF.keys())):
            # get the current key
            currentKey=list(categoryKeyFileDF.keys())[iKeys]
            # get the current list of record IDs
            currentRecordIDs=categoryKeyFileDF[currentKey]
            # create a list of the current category label repeated for the number of record IDs
            currentCategoryLabels=currentKey * len(currentRecordIDs)
            # create a temporary dataframe for the current key
            currentKeyDF=pd.DataFrame({'itemID':currentRecordIDs,'fieldValue':currentCategoryLabels})
            # append the temporary dataframe to the target dataframe using concat
            categoryKeyFileDF_temp=pd.concat([categoryKeyFileDF_temp,currentKeyDF],axis=0,ignore_index=True)
        # now set the categoryKeyFileDF to the categoryKeyFileDF_temp
        categoryKeyFileDF=categoryKeyFileDF_temp
    elif isinstance(categoryKeyFileDF,pd.DataFrame):
        # if the input category key file is already a pandas dataframe, then just set the categoryKeyFileDF variable to the input category key file
        categoryKeyFileDF=categoryKeyFileDF

    # go ahead and sort the categoryKeyFileDF by the recordID column, and then extract each column as a list (remember pandas is slow)
    categoryKeyFileDF=categoryKeyFileDF.sort_values(by='itemID')

    # NOTE:  one might think about trying to subset the categoryKeyFileDF now, so that we don't have to worry about working with records for categories we don't care about
    # HOWEVER we want the recordIDs to be of the same length as the designated axis of the input matrix so that we can use boolean masks / indexing.
    # this means that we need to do a check now to ensure that the labels of the target axis of inputDF are a subset of the 'recordIDs' in categoryKeyFileDF
    # if they aren't, then raise an error, if they are, then we subset the categoryKeyFileDF contents to only those records that are in the target axis of inputDF
    
    if targetAxis=='columns' or targetAxis==1 or targetAxis=='1':
        # get the target axis labels and treat them as a set
        targetAxisLabels=set(inputDF.columns)
        # get the record IDs from the categoryKeyFileDF and treat them as a set
        recordLabelsFromCategoryFile=set(categoryKeyFileDF['itemID'].values)
        # check if the target axis labels are a subset of the record labels
        if not targetAxisLabels.issubset(recordLabelsFromCategoryFile):
            # print the length of both sets
            print('The length of the target axis labels is: '+str(len(targetAxisLabels)))
            print('The length of the record labels from the category key file is: '+str(len(recordLabelsFromCategoryFile)))
            # also print their the elements that are in the target axis labels but not in the record labels from the category key file
            print('The elements in the target axis labels that are not in the record labels from the category key file are: '+str(targetAxisLabels.difference(recordLabelsFromCategoryFile)))
            # if they aren't, then raise an error
            raise ValueError('The target axis labels of the input matrix are not a subset of the record IDs in the categoryKeyFileDF.  This means that category assignments cannot be made for all records in the input matrix.')
        else:
            # if they are, then subset the categoryKeyFileDF to only those records in the target axis
            categoryKeyFileDF=categoryKeyFileDF[categoryKeyFileDF['itemID'].isin(targetAxisLabels)]
    elif targetAxis=='rows' or targetAxis==0 or targetAxis=='0':
        # get the target axis labels and treat them as a set
        targetAxisLabels=set(inputDF.index)
        # get the record IDs from the categoryKeyFileDF and treat them as a set
        recordLabelsFromCategoryFile=set(categoryKeyFileDF['itemID'].values)
        # check if the target axis labels are a subset of the record labels
        if not targetAxisLabels.issubset(recordLabelsFromCategoryFile):
            # print the length of both sets
            print('The length of the target axis labels is: '+str(len(targetAxisLabels)))
            print('The length of the record labels from the category key file is: '+str(len(recordLabelsFromCategoryFile)))
            # also print their the elements that are in the target axis labels but not in the record labels from the category key file
            print('The elements in the target axis labels that are not in the record labels from the category key file are: \n '+str(targetAxisLabels.difference(recordLabelsFromCategoryFile)))            # if they aren't, then raise an error
            raise ValueError('The target axis labels of the input matrix are not a subset of the record IDs in the categoryKeyFileDF.  This means that category assignments cannot be made for all records in the input matrix.')
        else:
            # if they are, then subset the categoryKeyFileDF to only those records in the target axis
            categoryKeyFileDF=categoryKeyFileDF[categoryKeyFileDF['itemID'].isin(targetAxisLabels)]
  
    # in order for the boolean mask to work, the mask must be of the same length as the axis of the input matrix
    # as such check to ensure that the axis specified in targetAxis for the input matrix is of the same length as the number of records in the (post subset) categoryKeyFileDF

    # check to ensure that the axis specified in targetAxis for the input matrix is of the same length as the number of records in the categoryKeyFileDF
    # if it is, then proceed
    if targetAxis=='columns' or targetAxis==1 or targetAxis=='1':
        if len(inputDF.columns)!=len(categoryKeyFileDF['itemID']):
            # print the lengths so the user can see what's going on
            print('The number of columns in the input matrix is ' + str(len(inputDF.columns)) + ' and the number of records in the categoryKeyFileDF is ' + str(len(categoryKeyFileDF['itemID'])))
            raise ValueError('The number of columns in the input matrix does not match the number of records in the categoryKeyFileDF.  This is likely due to a mismatch in the axis specified in the targetAxis variable.')
    elif targetAxis=='rows' or targetAxis==0 or targetAxis=='0':
        if len(inputDF.index)!=len(categoryKeyFileDF['itemID']):
            # print the lengths so the user can see what's going on
            print('The number of rows in the input matrix is ' + str(len(inputDF.index)) + ' and the number of records in the categoryKeyFileDF is ' + str(len(categoryKeyFileDF['itemID'])))
            raise ValueError('The number of rows in the input matrix does not match the number of records in the categoryKeyFileDF.  This is likely due to a mismatch in the axis specified in the targetAxis variable.')

    # get the unique category labels from the categoryKeyFileDF
    uniqueCategoryLabels=list(set(categoryKeyFileDF['fieldValue'].values))
    
    # go ahead and get both the recordIDs and the category labels from the categoryKeyFileDF as lists
    recordIDs=list(categoryKeyFileDF['itemID'].values)
    categoryLabels=list(categoryKeyFileDF['fieldValue'].values)

    # do a quick print report to indicate the number of records, unique categories, and the number of records per category
    print('There are ' + str(len(recordIDs)) + ' records in the categoryKeyFileDF, across ' + str(len(uniqueCategoryLabels)) + ' unique categories.')
    # print the number of records per category, with three such reports per line
    print('The number of records per category are:')
    for i in range(0,len(uniqueCategoryLabels),3):
        print(uniqueCategoryLabels[i] + ': ' + str(categoryLabels.count(uniqueCategoryLabels[i])),end=' ')
        if i+1<len(uniqueCategoryLabels):
            print(uniqueCategoryLabels[i+1] + ': ' + str(categoryLabels.count(uniqueCategoryLabels[i+1])),end=' ')
        if i+2<len(uniqueCategoryLabels):
            print(uniqueCategoryLabels[i+2] + ': ' + str(categoryLabels.count(uniqueCategoryLabels[i+2])),end=' ')
        print('')
    
    # create the output dataframe, which should retain the off-axis labels (e.g. the axis opposing the one specified in targetAxis), but will have the targetAxis labels replaced with the category labels
    if targetAxis=='columns':
        # we use float even though the values will be integers, because we want to be able to use NaN to indicate that a category is not present for a given record, for subsequent plotting purposes
        outputDF=pd.DataFrame(index=matrix.index,columns=uniqueCategoryLabels,dtype=float)
    elif targetAxis=='rows':
        # we use float even though the values will be integers, because we want to be able to use NaN to indicate that a category is not present for a given record, for subsequent plotting purposes
        outputDF=pd.DataFrame(index=uniqueCategoryLabels,columns=matrix.columns,dtype=float)
     
    # print statement indicating that the input variables have been checked and parsed, and that we are now moving to the subset-summation operation.
    print('Input variables have been checked and parsed, proceeding to indexer and intermediary array production.')    
    """
    Input variables have been checked and parsed, now we implement the subset-summation operation.
    """
    # print statment about precomputing and intermediary array production
    print('Precomputing indexers and creating intermediary arrays.')
    # here we'll do a few pre-merge operations to speed things up
    # in accordance with this stackoverflow post: https://stackoverflow.com/questions/54767327/pandas-performance-columns-selection
    # we probably want to avoid using .loc to select columns, as it is slow.
    # I'm not sure, but we may even want to avoid using a list of column indexes, and thus instead use a boolean mask to select the columns we want.
    # to this end, let's create a dictionary of boolean masks, where the keys are the unique category labels, and the values are the boolean masks for the columns that are assigned that category label in the categoryKeyFileDF (and presumably the input matrix as well, now that it has been sorted)
    # We'll use .isin(), and treat the (now sorted) categoryKeyFileDF['itemID'] content as a np.array for speed
    boolMaskDict={}
    # create np.array of the categoryKeyFileDF['fieldValue'] (i.e. the category labels) content
    categoryLabelsArray=np.array(list(categoryKeyFileDF['fieldValue'].values))
    for i in range(len(uniqueCategoryLabels)):
        # generate bool vector corresponding to whether uniqueCategoryLabels == each element in categoryLabelsArray
        # do this in the fastest way possible, which is to use np.char.equal, which seems to be about 50 times faster than list comprehension
        currentBoolMask=np.char.equal(np.asarray(uniqueCategoryLabels[i]),categoryLabelsArray)
        # add this bool mask to the dictionary
        boolMaskDict[uniqueCategoryLabels[i]]=currentBoolMask

    # now that we have done this, we should have the correct indexers for the input matrix.
    # however to speed up the operation further, we should convert the content of the input matrix to a np.array
    # we can do this by using the .values attribute of the input matrix
    matrixContentAsArray=matrix.values
    # print statement indicating that we have precomputed the indexers and created the intermediary arrays
    print('Indexer and intermediary array creation complete, proceeding to subset-summation operation.')
    # initiate timer for subset-summation operation
    subsetSummationTimerStart=time.time()
    for i in range(len(uniqueCategoryLabels)):
        # first extract the current bool mask
        currentBoolMask=boolMaskDict[uniqueCategoryLabels[i]]
        # now we can use this bool mask to select the appropriate columns from the matrixContentAsArray
        # we can then sum the columns of this submatrix to get the subset-summation for the current category label
        if targetAxis=='columns':
            # we use np.nansum() here to ignore NaN values
            currentSubsetSum=np.nansum(matrixContentAsArray[:,currentBoolMask],axis=1)
            # now we can assign this subset sum to the appropriate column of the outputDF
            outputDF[uniqueCategoryLabels[i]]=currentSubsetSum
        elif targetAxis=='rows':
            # we use np.nansum() here to ignore NaN values
            currentSubsetSum=np.nansum(matrixContentAsArray[currentBoolMask,:],axis=0)
            # now we can assign this subset sum to the appropriate row of the outputDF
            outputDF.loc[uniqueCategoryLabels[i]]=currentSubsetSum
    # stop timer for subset-summation operation
    subsetSummationTimerStop=time.time()
    # print statement indicating that the subset-summation operation is complete
    print('Subset-summation operation complete in ' + str(subsetSummationTimerStop-subsetSummationTimerStart) + ' seconds.')
    # return the outputDF
    
    # determine the desired saving behavior, stealing this code from coOccurrenceMatrix
    if savePath is not None:
        # we don't need to run a check here to determine if the rows and indexes are meaningful
        # they *have* to be, given the above algorithm

        # if it's not none, then check it if is blank (''), or a specific format
        if savePath=='':
            # if it's blank, then they haven't provided a desired format, so we have to use a heuristic for this
            # we'll just set an arbitrary value here, to serve as the heuristic limit
            # in this case, what the value represents is the number of rows (or columns) that we would consider the maximum reasonable to store in a csv
            # in essence: if there are sufficiently few values, then it's fine to store the data as an uncompressed csv.
            # for example, a 1000 by 1000 matrix would be 1,000,000 numeric values which would be 8,000,000 bytes, or 8 MB for float 64 (or 4 MB for float 32)
            thresholdCSV=1000
            # also set the string for the default name
            defaultName='categorySumMergeMatrix'
            # if the number of rows or columns is less than the threshold, then save as a csv
            if outputDF.shape[0]<thresholdCSV:          
                # save the sumMergeMatrix matrix as a csv
                outputDF.to_csv(defaultName+'.csv')
                print('Saved sumMergeMatrix matrix as a csv to \n' + defaultName+'.csv')
            # if the number of rows or columns is greater than the threshold, then save as an hdf5
            else:
                import h5py
                # save the co-occurrence matrix as an hdf5
                with h5py.File(defaultName+'.hdf5','w') as f:
                    f.create_dataset('dataMatrix',data=outputDF.values,compression='gzip')
                    f.create_dataset('rowName',data=outputDF.index,compression='gzip')
                    f.create_dataset('colName',data=outputDF.columns,compression='gzip')
                # now close the file
                f.close()
                print('Saved sumMergeMatrix matrix as an hdf5 to \n' + defaultName+'.hdf5')
        # if it's not blank, then check if it's a csv or an hdf5
        elif savePath.endswith('.csv'):
            # if it's a csv, then save the co-occurrence matrix as a csv essentially the same way as above
            outputDF.to_csv(savePath)
            print('Saved sumMergeMatrix matrix as a csv to \n' + savePath)

        elif savePath.endswith('.hdf5') or savePath.endswith('.h5') or savePath.endswith('.hdf'):
            import h5py
            # if it's an hdf5, then save the co-occurrence matrix as an hdf5 essentially the same way as above
            with h5py.File(defaultName+'.hdf5','w') as f:
                f.create_dataset('dataMatrix',data=outputDF.values,compression='gzip')
                f.create_dataset('rowName',data=outputDF.index,compression='gzip')
                f.create_dataset('colName',data=outputDF.columns,compression='gzip')
                # now close the file
                f.close()
                print( 'Saved sumMergeMatrix matrix as an hdf5 to \n' + savePath)
        # if it's not blank, csv, or hdf5, or None then raise an error
        else:
            raise ValueError('The savePath variable must be either blank (''), None, or end with ".csv" or ".hdf5"')

    return outputDF

def categoryCoocurrenceCosineDistanceMatrix(inputMatrixDF, categoryKeyFileDF, targetAxis='columns',savePath=''):
    """
    This function takes in a whole dataset matrix and a category key file, and computes the cosine distance metric between each category for the flattened
    cooccurrence matrix (term-term) associated with each category.  The results are returned as a square matrix with the rows and columns corresponding to the categories.

    Parameters
    ----------
    inputMatrixDF : pandas dataframe
        A matrix of some sort, which contains numeric values.  The column labels and row indexes should correspond to the
        identifiers of the elements of the specified axis.  They will be used to label the rows and columns of the output matrix.
    categoryKeyFileDF : pandas dataframe
        A dataframe containing the category key file.  This should have two columns, one containing the 'itemIDs', and the other containing the category labels as 'fieldValue'.
    targetAxis : string
        Either 'rows' or 'columns', depending on whether you want to compute the cosine distance between the rows or the columns of the input inputMatrixDF.
    savePath : string
        The path to which the results should be saved.  If left blank, the results will not be saved.
    
    Returns
    -------
    outputDF : pandas dataframe
        A square matrix with the rows and columns corresponding to the categories.  The values are the cosine distance between the flattened cosine matrices
        associated with each category.

    import h5py
    import pandas as pd
    inputMatrixDFPath= '/media/dan/HD4/coding/gitDir/USG_grants_crawl/inputData/grantsGov/analyzed/thresholdedData.hd5'
    # load it
    loadedHDF5obj=h5py.File(inputMatrixDFPath,'r')
    inputMatrixDF=pdDataFrameFromHF5obj(loadedHDF5obj[list(loadedHDF5obj.keys())[0]])
    categoryKeyFileDFpath='/media/dan/HD4/coding/gitDir/USG_grants_crawl/inputData/grantsGov/analyzed/agencyExtract.csv'
    categoryKeyFileDF=pd.read_csv(categoryKeyFileDFpath,dtype=str)
    
    """
    import pandas as pd
    import numpy as np
    import scipy.spatial.distance as ssd
    import timeit

    # we're going to use timeit to time each step of this process

    # obtain the list of unique category labels using set

    uniqueCategoryLabels=list(set(categoryKeyFileDF['fieldValue']))

    def quickMaskUpperTriangle(inputArray,includeDiagonal=True):
        """
        This function takes in a square matrix and returns a mask of the upper triangle of the matrix.
        Depending on whether the includeDiagonal variable is set to True or False, the diagonal will be included or not.
        
        Parameters
        ----------
        inputArray : numpy array
            A square matrix.
        includeDiagonal : boolean
            Whether or not to include the diagonal of the matrix in the mask.

        Returns
        -------
        outputArray : numpy array
            A boolean mask of the upper triangle of the input matrix.

        Test Method
        -----------
        # lets test this for desired behavior
        # create a test array of random integers
        testArray=np.random.randint(0,10,(5,5))
        # print the test array
        print('testArray=\n',testArray)
        # print the upper triangle of the test array
        print('upper triangle of testArray=\n',quickMaskUpperTriangle(testArray,includeDiagonal=True))
        # print the upper triangle of the test array, not including the diagonal
        print('upper triangle of testArray, not including the diagonal=\n',quickMaskUpperTriangle(testArray,includeDiagonal=False))
        

        """
        # get the shape of the input array
        inputArrayShape=inputArray.shape[0]
        # create a range of values from 0 to the shape of the input array
        rangeArray=np.arange(inputArrayShape)
        # create a mask of the upper triangle of the input array
        if includeDiagonal==True:
            mask = rangeArray[:,None] <= rangeArray
        elif includeDiagonal==False:
            mask = rangeArray[:,None] < rangeArray
        # return the mask
        return inputArray[mask]


    # we're going to iterate across these to create a list of flattened cosine matrices
    # First we'll subset the input inputMatrixDF using fastSubsetDF_by_categoryKeyFile(inputDF,targetAxis,categoryKeyFile,categoryToExtract)
    # then we'll use the cosineDistanceMatrix(inputMatrixDF,axisToCompareWithin='columns',savePath='') function to compute the cosine distance matrix for the subsetted inputMatrixDF
    # then we'll flatten the cosine distance matrix and add it to the storage array, wherein the
    # rows correspond to the categories and the number of columns corresponds to the length of the flattened cosine distance matrix
    # initialize an array of zeros to store the flattened cosine matrices
    # HOWEVER, lets only do this for the upper triangle of the matrix, NOT including the diagonal itself, since the lower triangle is just the same values
    if targetAxis=='columns':
        # The size of the intermediary arrays is actually determined by the OFF target axis, insofar as 
        # the targetAxis variable is indicating the axis whose elements have category memberships and should thus be subsetted
        # as the output will actually be a square matrix with the rows and columns corresponding to the off target axis
        # so if the targetAxis is columns, then the intermediary arrays will be rows by rows (i.e. the number of rows in the inputMatrixDF)
        # but even here, we have redundancy, since the lower triangle of the matrix is just the same values, so all
        # we really want is the upper triangle, WITHOUT the diagonal itself, since that's just 1's
        # so first we compute the number of indicies in the upper triangle of the matrix (without the diagonal)
        # do this by creating a dummy matrix of all ones of the appropriate size, and then use the quickMaskUpperTriangle function to get the upper triangle mask, and then summing the mask
        dummyMask=np.ones((len(inputMatrixDF.index),len(inputMatrixDF.index)))
        upperTriangleIndexCount=int(np.sum(quickMaskUpperTriangle(dummyMask,includeDiagonal=False)))
        # then we initialize the flattenedCosineMatrixArray to be a matrix with the number of rows equal to the number of unique category labels
        # and the number of columns equal to the number of indicies in the upper triangle of the matrix (without the diagonal)
        flattenedCosineMatrixArray=np.zeros((len(uniqueCategoryLabels),upperTriangleIndexCount))
    elif targetAxis=='rows':
        dummyMask=np.ones((len(inputMatrixDF.columns),len(inputMatrixDF.columns)))
        upperTriangleIndexCount=int(np.sum(quickMaskUpperTriangle(dummyMask,includeDiagonal=False)))
        # then we initialize the flattenedCosineMatrixArray to be a matrix with the number of rows equal to the number of unique category labels
        # and the number of columns equal to the number of indicies in the upper triangle of the matrix (without the diagonal)
        flattenedCosineMatrixArray=np.zeros((len(uniqueCategoryLabels),upperTriangleIndexCount))

    for i in range(len(uniqueCategoryLabels)):
        # subset the inputMatrixDF using fastSubsetDF_by_categoryKeyFile(inputDF,targetAxis,categoryKeyFile,categoryToExtract)
        currentSubsetDF=fastSubsetDF_by_categoryKeyFile(inputMatrixDF,targetAxis,categoryKeyFileDF,uniqueCategoryLabels[i])
        # remember, we are trying to generate a term-term matrix, so instead of doing columns, which would be the recordIDs
        # we want to do rows, which would be the terms
        # if the matrix is not full of zeros, then compute the cosine distance matrix
        if currentSubsetDF.values.any()==True:
            if targetAxis=='columns':
                currCooccurrenceMatrix=coOccurrenceMatrix(currentSubsetDF,rowsOrColumns='rows',savePath=None)
                #currentCosineDistanceMatrix=cosineDistanceMatrix(currentSubsetDF,axisToCompareWithin='rows',savePath='')
            elif targetAxis=='rows':
                currCooccurrenceMatrix=coOccurrenceMatrix(currentSubsetDF,rowsOrColumns='columns',savePath=None)
                #currentCosineDistanceMatrix=cosineDistanceMatrix(currentSubsetDF,axisToCompareWithin='columns',savePath='')
            # print the shape of the currentCosineDistanceMatrix
            # if currCooccurrenceMatrix is full of zeros, print the current category label and how many columns are in currentSubsetDF
            # check if any on a boolean matrix returns True or False
            # start with currCooccurrenceMatrix=np.zeros((100,100 ))
            
            if currCooccurrenceMatrix.any()==False:
                print('currCooccurrenceMatrix is full of zeros for category ' + str(uniqueCategoryLabels[i]) + ' with ' + str(len(currentSubsetDF.columns)) + ' columns')   

            # from this current cosine distance matrix, we want to extract the upper triangle of the matrix, excluding the diagonal
            # we'll use the quickMaskUpperTriangle(inputArray,includeDiagonal=False) function to do this
            # get the masked results
            currentMaskedResults=quickMaskUpperTriangle(currCooccurrenceMatrix,includeDiagonal=False)
            # from this, get only the non-masked values and flatten them
            flattenedCosineMatrixArray[i,:]=currentMaskedResults
        # otherwise, if the matrix is full of zeros, then we'll just add a row of zeros to the flattenedCosineMatrixArray
        elif currentSubsetDF.values.any()==False:
            flattenedCosineMatrixArray[i,:]=np.zeros((1,upperTriangleIndexCount))

    # print curent status
    print('Within-category co-occurrence matrices computed for ' + str(len(uniqueCategoryLabels)) + ' categories')


    # now that we have the list of flattened cosine matrices, we can compute the cosine distance between each pair of categories
    # we'll place the results in a numpy array
    # first we'll create an empty numpy array of the appropriate size
    outputArray=np.zeros((len(uniqueCategoryLabels),len(uniqueCategoryLabels)))
    # now we'll iterate across the flattened cosine matrix list and compute the cosine distance between each pair of categories
    for i in range(len(uniqueCategoryLabels)):
        for j in range(len(uniqueCategoryLabels)):
            # compute the cosine distance between the two flattened cosine matrices
            #currentCosineDistance=ssd.cosine(flattenedCosineMatrixList[i],flattenedCosineMatrixList[j])
            currentCosineDistance=fastNumbaCosinSimilarity(flattenedCosineMatrixArray[i,:],flattenedCosineMatrixArray[j,:])
            # add this value to the outputArray
            outputArray[i,j]=currentCosineDistance
            # stop timer

    # print curent status
    print('Between-category cosine distance matrices computed for ' + str(len(uniqueCategoryLabels)) + ' categories')

    # now we can convert the outputArray to a pandas dataframe, and label the rows and columns with the category labels
    outputDF=pd.DataFrame(outputArray,index=uniqueCategoryLabels,columns=uniqueCategoryLabels)
    return outputDF

def categoryCosineDistanceMatrix(inputMatrixDF, categoryKeyFileDF, targetAxis='columns',savePath=''):
    """
    This function takes in a whole dataset matrix and a category key file, and computes the cosine distance metric between each category for the flattened
    cosine matrix associated with each category.  The results are returned as a square matrix with the rows and columns corresponding to the categories.

    Parameters
    ----------
    inputMatrixDF : pandas dataframe
        A matrix of some sort, which contains numeric values.  The column labels and row indexes should correspond to the
        identifiers of the elements of the specified axis.  They will be used to label the rows and columns of the output matrix.
    categoryKeyFileDF : pandas dataframe
        A dataframe containing the category key file.  This should have two columns, one containing the 'itemIDs', and the other containing the category labels as 'fieldValue'.
    targetAxis : string
        Either 'rows' or 'columns', depending on whether you want to compute the cosine distance between the rows or the columns of the input inputMatrixDF.
    savePath : string
        The path to which the results should be saved.  If left blank, the results will not be saved.
    
    Returns
    -------
    outputDF : pandas dataframe
        A square matrix with the rows and columns corresponding to the categories.  The values are the cosine distance between the flattened cosine matrices
        associated with each category.

    import h5py
    import pandas as pd
    inputMatrixDFPath= '/media/dan/HD4/coding/gitDir/USG_grants_crawl/inputData/grantsGov/analyzed/thresholdedData.hd5'
    # load it
    loadedHDF5obj=h5py.File(inputMatrixDFPath,'r')
    inputMatrixDF=pdDataFrameFromHF5obj(loadedHDF5obj[list(loadedHDF5obj.keys())[0]])
    categoryKeyFileDFpath='/media/dan/HD4/coding/gitDir/USG_grants_crawl/inputData/grantsGov/analyzed/agencyExtract.csv'
    categoryKeyFileDF=pd.read_csv(categoryKeyFileDFpath,dtype=str)
    
    """
    import pandas as pd
    import numpy as np
    import scipy.spatial.distance as ssd
    import timeit

    # we're going to use timeit to time each step of this process

    # obtain the list of unique category labels using set

    uniqueCategoryLabels=list(set(categoryKeyFileDF['fieldValue']))

    def quickMaskUpperTriangle(inputArray,includeDiagonal=True):
        """
        This function takes in a square matrix and returns a mask of the upper triangle of the matrix.
        Depending on whether the includeDiagonal variable is set to True or False, the diagonal will be included or not.
        
        Parameters
        ----------
        inputArray : numpy array
            A square matrix.
        includeDiagonal : boolean
            Whether or not to include the diagonal of the matrix in the mask.

        Returns
        -------
        outputArray : numpy array
            A boolean mask of the upper triangle of the input matrix.

        Test Method
        -----------
        # lets test this for desired behavior
        # create a test array of random integers
        testArray=np.random.randint(0,10,(5,5))
        # print the test array
        print('testArray=\n',testArray)
        # print the upper triangle of the test array
        print('upper triangle of testArray=\n',quickMaskUpperTriangle(testArray,includeDiagonal=True))
        # print the upper triangle of the test array, not including the diagonal
        print('upper triangle of testArray, not including the diagonal=\n',quickMaskUpperTriangle(testArray,includeDiagonal=False))
        

        """
        # get the shape of the input array
        inputArrayShape=inputArray.shape[0]
        # create a range of values from 0 to the shape of the input array
        rangeArray=np.arange(inputArrayShape)
        # create a mask of the upper triangle of the input array
        if includeDiagonal==True:
            mask = rangeArray[:,None] <= rangeArray
        elif includeDiagonal==False:
            mask = rangeArray[:,None] < rangeArray
        # return the mask
        return inputArray[mask]


    # we're going to iterate across these to create a list of flattened cosine matrices
    # First we'll subset the input inputMatrixDF using fastSubsetDF_by_categoryKeyFile(inputDF,targetAxis,categoryKeyFile,categoryToExtract)
    # then we'll use the cosineDistanceMatrix(inputMatrixDF,axisToCompareWithin='columns',savePath='') function to compute the cosine distance matrix for the subsetted inputMatrixDF
    # then we'll flatten the cosine distance matrix and add it to the storage array, wherein the
    # rows correspond to the categories and the number of columns corresponds to the length of the flattened cosine distance matrix
    # initialize an array of zeros to store the flattened cosine matrices
    # HOWEVER, lets only do this for the upper triangle of the matrix, NOT including the diagonal itself, since the lower triangle is just the same values
    if targetAxis=='columns':
        # The size of the intermediary arrays is actually determined by the OFF target axis, insofar as 
        # the targetAxis variable is indicating the axis whose elements have category memberships and should thus be subsetted
        # as the output will actually be a square matrix with the rows and columns corresponding to the off target axis
        # so if the targetAxis is columns, then the intermediary arrays will be rows by rows (i.e. the number of rows in the inputMatrixDF)
        # but even here, we have redundancy, since the lower triangle of the matrix is just the same values, so all
        # we really want is the upper triangle, WITHOUT the diagonal itself, since that's just 1's
        # so first we compute the number of indicies in the upper triangle of the matrix (without the diagonal)
        # do this by creating a dummy matrix of all ones of the appropriate size, and then use the quickMaskUpperTriangle function to get the upper triangle mask, and then summing the mask
        dummyMask=np.ones((len(inputMatrixDF.index),len(inputMatrixDF.index)))
        upperTriangleIndexCount=int(np.sum(quickMaskUpperTriangle(dummyMask,includeDiagonal=False)))
        # then we initialize the flattenedCosineMatrixArray to be a matrix with the number of rows equal to the number of unique category labels
        # and the number of columns equal to the number of indicies in the upper triangle of the matrix (without the diagonal)
        flattenedCosineMatrixArray=np.zeros((len(uniqueCategoryLabels),upperTriangleIndexCount))
    elif targetAxis=='rows':
        dummyMask=np.ones((len(inputMatrixDF.columns),len(inputMatrixDF.columns)))
        upperTriangleIndexCount=int(np.sum(quickMaskUpperTriangle(dummyMask,includeDiagonal=False)))
        # then we initialize the flattenedCosineMatrixArray to be a matrix with the number of rows equal to the number of unique category labels
        # and the number of columns equal to the number of indicies in the upper triangle of the matrix (without the diagonal)
        flattenedCosineMatrixArray=np.zeros((len(uniqueCategoryLabels),upperTriangleIndexCount))




    for i in range(len(uniqueCategoryLabels)):
        # subset the inputMatrixDF using fastSubsetDF_by_categoryKeyFile(inputDF,targetAxis,categoryKeyFile,categoryToExtract)
        currentSubsetDF=fastSubsetDF_by_categoryKeyFile(inputMatrixDF,targetAxis,categoryKeyFileDF,uniqueCategoryLabels[i])
        # remember, we are trying to generate a term-term matrix, so instead of doing columns, which would be the recordIDs
        # we want to do rows, which would be the terms
        if targetAxis=='columns':
            currentCosineDistanceMatrix=cosineDistanceMatrix(currentSubsetDF,axisToCompareWithin='rows')
        elif targetAxis=='rows':
            currentCosineDistanceMatrix=cosineDistanceMatrix(currentSubsetDF,axisToCompareWithin='columns')
        # print the shape of the currentCosineDistanceMatrix

        # from this current cosine distance matrix, we want to extract the upper triangle of the matrix, excluding the diagonal
        # we'll use the quickMaskUpperTriangle(inputArray,includeDiagonal=False) function to do this
        # get the masked results
        currentMaskedResults=quickMaskUpperTriangle(currentCosineDistanceMatrix,includeDiagonal=False)
        # from this, get only the non-masked values and flatten them
        flattenedCosineMatrixArray[i,:]=currentMaskedResults

    # print curent status
    print('Within-category cosine distance matrices computed for ' + str(len(uniqueCategoryLabels)) + ' categories')


    # now that we have the list of flattened cosine matrices, we can compute the cosine distance between each pair of categories
    # we'll place the results in a numpy array
    # first we'll create an empty numpy array of the appropriate size
    outputArray=np.zeros((len(uniqueCategoryLabels),len(uniqueCategoryLabels)))
    # now we'll iterate across the flattened cosine matrix list and compute the cosine distance between each pair of categories
    for i in range(len(uniqueCategoryLabels)):
        for j in range(len(uniqueCategoryLabels)):
            # compute the cosine distance between the two flattened cosine matrices
            #currentCosineDistance=ssd.cosine(flattenedCosineMatrixList[i],flattenedCosineMatrixList[j])
            currentCosineDistance=fastNumbaCosinSimilarity(flattenedCosineMatrixArray[i,:],flattenedCosineMatrixArray[j,:])
            # add this value to the outputArray
            outputArray[i,j]=currentCosineDistance
            # stop timer

    # print curent status
    print('Between-category cosine distance matrices computed for ' + str(len(uniqueCategoryLabels)) + ' categories')

    # now we can convert the outputArray to a pandas dataframe, and label the rows and columns with the category labels
    outputDF=pd.DataFrame(outputArray,index=uniqueCategoryLabels,columns=uniqueCategoryLabels)
    return outputDF

def generatePermutatedCategoryCosineDistanceMatrices(inputMatrixDF, categoryKeyFileDF, targetAxis='columns',numPermutations=100,):
    """
    This function is used to create a set of permutated category cosine distance matrices.  Specifically, the category assignments specified in the category key file
    are randomly permuted, and the cosine distance matrix is computed for each permutation.  The results are returned as a 3D numpy array, with the first dimension
    corresponding to the permutation number, and the second and third dimensions corresponding to the rows and columns of the cosine distance matrix.

    Parameters
    ----------
    inputMatrixDF : pandas dataframe
        A matrix of some sort, which contains numeric values.  The column labels and row indexes should correspond to the
        identifiers of the elements of the specified axis.  They will be used to label the rows and columns of the output matrix.
    categoryKeyFileDF : pandas dataframe
        A dataframe containing the category key file.  This should have two columns, one containing the 'itemIDs', and the other containing the category labels as 'fieldValue'.
    targetAxis : string
        Either 'rows' or 'columns', depending on whether you want to compute the cosine distance between the rows or the columns of the input inputMatrixDF.
    
    Returns
    -------
    outputArray : numpy array
        A 3D numpy array, with the first dimension corresponding to the permutation number, and the second and third dimensions corresponding to the rows and columns of the cosine distance matrix.

    """
    # import necessary modules
    import pandas as pd
    import numpy as np
    import scipy.spatial.distance as ssd
    import random
    import sys

    # create the output np array, which does not depend on the targetAxis, because the matrix generated by currentCosineDistanceMatrix
    # will condense the specified axis of inputMatrixDF down to the unique category labels, and then compute the cosine distance matrix using the 
    # associated values found from the off target axis (which theoretically should be small)
    # so we'll just create the output array using the number of unique category labels
    
    # create a print statement to indicate the size of the array being created
    print('Creating output array of size: '+str(numPermutations)+' x '+str(len(set(categoryKeyFileDF['fieldValue'])))+' x '+str(len(set(categoryKeyFileDF['fieldValue']))))
    outputArray=np.zeros((numPermutations,len(set(categoryKeyFileDF['fieldValue'])),len(set(categoryKeyFileDF['fieldValue']))))
    # print report on the size of the array
    print('Output array for '+ str(numPermutations)+' permutations of will be of size: '+str(sys.getsizeof(outputArray)/1000000)+' MB')

    # obtain the counts for each category label
    categoryCounts=categoryKeyFileDF['fieldValue'].value_counts()
    # get a copied list of the category labels, which should come from categoryKeyFileDF['fieldValue']
    categoryLabels=categoryKeyFileDF['fieldValue'].copy().tolist()

    # begin the permutation loop
    for i in range(numPermutations):
        # print the current permutation number and replace the previous print of the permutation number
        print('Permutation number: '+str(i+1)+' of '+str(numPermutations))
        # shuffle the category labels of categoryKeyFileDF, as found in the `fieldValue` column
        categoryKeyFileDF_shuffled=categoryKeyFileDF.copy()
        # the sampling should be done such that the frequency of each category label is preserved
        # this can be done by sampling categoryLabels without replacement, and then assigning the sampled category labels to the categoryKeyFileDF_shuffled
        categoryKeyFileDF_shuffled['fieldValue']=random.sample(categoryLabels,len(categoryLabels))
        # compute the cosine distance matrix for the permuted categoryKeyFileDF_shuffled using categoryCosineDistanceMatrix(inputMatrixDF, categoryKeyFileDF, targetAxis='columns',savePath='')
        currentCosineDistanceMatrix=categoryCoocurrenceCosineDistanceMatrix(inputMatrixDF, categoryKeyFileDF_shuffled, targetAxis=targetAxis,savePath='')
        # add the currentCosineDistanceMatrix to the outputArray
        outputArray[i,:,:]=currentCosineDistanceMatrix.values

    return outputArray

def categoryCosinePermutationTest(inputMatrixDF, categoryKeyFileDF, targetAxis='columns',numPermutations=100,zScoreSavePath='',stdSavePath=None,meanSavePath=None):
    """
    This function runs a permutation test to determine whether the cosine distance between categories is significantly different than would be expected by chance.
    Specifically, the category assignments specified in the category key file are randomly permuted, and the cosine distance matrix is computed for each permutation.
    The cosine distance matrix for the actual category assignments is then compared to the distribution of cosine distance measures (across permutations, but within category-category pairs).
    The resultant z-scores are returned in a correspondingly shaped pandas dataframe.

    Parameters
    ----------
    inputMatrixDF : pandas dataframe
        A matrix of some sort, which contains numeric values.  The column labels and row indexes should correspond to the
        identifiers of the elements of the specified axis.  They will be used to label the rows and columns of the output matrix.
        The category key file should contain a column, 'itemIDs', which contains axis labels that correspond to the indicated axis (via `targetAxis`) of the inputMatrixDF.
    categoryKeyFileDF : pandas dataframe
        A dataframe containing the category key file.  This should have two columns, one containing the 'itemIDs', and the other containing the category labels as 'fieldValue'.
    targetAxis : string
        Either 'rows' or 'columns', depending on whether you want to compute the cosine distance between the rows or the columns of the input inputMatrixDF.
    numPermutations : int
        The number of permutations to perform.
    zScoreSavePath : string
        The path to save the z-scores dataframe to. If None, then the z-scores dataframe will not be saved. If '', then the z-scores dataframe will be saved to the current working directory.
    stdSavePath : string
        The path to save the standard deviation dataframe to.  If None, then the standard deviation dataframe will not be saved.
    meanSavePath : string
        The path to save the mean dataframe to. If None, then the mean dataframe will not be saved.

    Returns
    -------
    outputDF : pandas dataframe
        A pandas dataframe containing the z-scores for each category-category pair.
    
    """
    import pandas as pd
    import numpy as np

    # perform the permutation test using generatePermutatedCategoryCosineDistanceMatrices(inputMatrixDF, categoryKeyFileDF, targetAxis='columns',numPermutations=100)
    permutationResults=generatePermutatedCategoryCosineDistanceMatrices(inputMatrixDF, categoryKeyFileDF, targetAxis=targetAxis,numPermutations=numPermutations)
    # compute the mean and standard deviation of the permutationResults, for permutation results which are not all zero

    # as a temporary debug method we will save down the permutationResults array
    np.save('permutationResults.npy',permutationResults)

    # compute the mean and standard deviations for these
    permutationMean=np.mean(permutationResults,axis=0)
    permutationStd=np.std(permutationResults,axis=0)

    # compute the actual cosine distance matrix using categoryCosineDistanceMatrix(inputMatrixDF, categoryKeyFileDF, targetAxis='columns',savePath='')
    # remember, it's output is a pandas dataframe
    actualCosineDistanceMatrix=categoryCoocurrenceCosineDistanceMatrix(inputMatrixDF, categoryKeyFileDF, targetAxis=targetAxis,savePath='')
    actualCosineResultsArray=actualCosineDistanceMatrix.values

    # also temporarily save down the actualCosineResultsArray
    np.save('actualCosineResultsArray.npy',actualCosineResultsArray)

    # compute the z-scores using numpy functions, remember though, some of the standard deviations that were create
    # may be zero, so we need to check for that and replace them with 1's temporarily
    # this is because we are dividing by the standard deviation, and dividing by zero is not allowed
    tempStd=permutationStd.copy()
    tempStd[tempStd==0]=1
    zScores=np.divide(np.subtract(actualCosineResultsArray,permutationMean),tempStd)
    # convert the z-scores to a pandas dataframe
    if targetAxis=='columns':
        outputDF=pd.DataFrame(zScores,index=actualCosineDistanceMatrix.columns,columns=actualCosineDistanceMatrix.columns)
        meanDF=pd.DataFrame(permutationMean,index=actualCosineDistanceMatrix.columns,columns=actualCosineDistanceMatrix.columns)
        stdDF=pd.DataFrame(permutationStd,index=actualCosineDistanceMatrix.columns,columns=actualCosineDistanceMatrix.columns)
    elif targetAxis=='rows':
        outputDF=pd.DataFrame(zScores,index=actualCosineDistanceMatrix.index,columns=actualCosineDistanceMatrix.index)
        meanDF=pd.DataFrame(permutationMean,index=actualCosineDistanceMatrix.index,columns=actualCosineDistanceMatrix.index)
        stdDF=pd.DataFrame(permutationStd,index=actualCosineDistanceMatrix.index,columns=actualCosineDistanceMatrix.index)

    # save the z-scores dataframe to the specified path
    if zScoreSavePath is not None:
        outputDF.to_csv(zScoreSavePath)
    # save the mean dataframe to the specified path
    if meanSavePath is not None:
        meanDF.to_csv(meanSavePath)
    # save the standard deviation dataframe to the specified path
    if stdSavePath is not None:
        stdDF.to_csv(stdSavePath)

    return outputDF

def assignHigherOrderCategoryToKeyFile(categoryKeyFileDF,augmentKeyfile,higherOrderColumn=0,existingCategoryColumn=1):
    """
    This function augments a categoryKeyFileDF, which is typically understood to have one column (the first) indicating
    the category membership of the records, with the second column actually indicating the record IDs.  As obtained from 
    fieldExtractAndSave of this package, the column names would be 'fieldValue' and 'itemIDs', respectively.
    
    Parameters
    ----------
    categoryKeyFileDF : pandas dataframe
        A dataframe containing the category key file.  This should have two columns, one containing the 'itemIDs', and the other containing the category labels as 'fieldValue'.
    augmentKeyfile : pandas dataframe
        A dataframe containing an augmentation of the category key file.  It should map the existing categories onto higher order categories.
    higherOrderColumn : int
        The column of the augmentKeyfile that contains the higher order category labels.
    existingCategoryColumn : int
        The column of the augmentKeyfile that contains the existing category labels.
    """

    import pandas as pd
    import numpy as np

    # 

    # get all four columns (e.g. two from each dataframe) as arrays
    existingCategories=np.asarray(categoryKeyFileDF.iloc[:,['fieldValue']].values)
    existingItemIDs=np.asarray(categoryKeyFileDF.iloc[:,['itemIDs']].values)
    higherOrderCategories=np.asarray(augmentKeyfile.iloc[:,[higherOrderColumn]].values)
    existingCategories=np.asarray(augmentKeyfile.iloc[:,[existingCategoryColumn]].values)

    # iterate across the unique values of existingCategories and obtain the indexes of existingItemIDs that
    # correspond to each unique value, store these in a dictionary
    # get the unique existingCategories
    uniqueExistingCategories=np.unique(existingCategories)
    existingCategoryIndexesDict={}
    for i in range(len(uniqueExistingCategories)):
        existingCategoryIndexesDict[uniqueExistingCategories[i]]=np.where(existingCategories==uniqueExistingCategories[i])[0]

    # essentially do the same thing for higherOrderCategories, but this time we're storing the indexes of uniqueExistingCategories
    # that correspond to each unique value of higherOrderCategories
    uniqueHigherOrderCategories=np.unique(higherOrderCategories)
    higherOrderCategoryIndexesDict={}
    for i in range(len(uniqueHigherOrderCategories)):
        higherOrderCategoryIndexesDict[uniqueHigherOrderCategories[i]]=np.where(higherOrderCategories==uniqueHigherOrderCategories[i])[0]

    # our goal is produce an ouput df, that once more has 'fieldValue' and 'itemIDs' columns, but this time the 'fieldValue' column
    # will contain the higher order categories, and the 'itemIDs' column will contain the itemIDs of the existing categories
    # we'll start by creating a mapping dictionary, that iterates across higherOrderCategoryIndexesDict, obtains the categories
    # that are associated with it, and uses these to obtain the itemIDs from existingCategoryIndexesDict
    mappingDict={}
    for i in range(len(uniqueHigherOrderCategories)):
        # get the existing categories that are associated with this higher order category
        currentExistingCategories=higherOrderCategoryIndexesDict[uniqueHigherOrderCategories[i]]
        # iterate across these and obtain the itemIDs from existingCategoryIndexesDict
        itemIDs=[]
        for j in range(len(currentExistingCategories)):
            itemIDs.append(existingCategoryIndexesDict[currentExistingCategories[j]])
        # store these in the mappingDict
        mappingDict[uniqueHigherOrderCategories[i]]=itemIDs

    # now we can create the output dataframe
    # start by creating two arrays to hold the values for the two columns, they should be of length equal to the number of rows in the output dataframe
    # and of dtype object to accomidate strings
    outDF=pd.DataFrame(columns=['fieldValue','itemIDs'])
    # iterate across the keys of mappingDict, and use them to populate the output arrays
    for i in range(len(mappingDict.keys())):
        # get the higher order category
        currentHigherOrderCategory=list(mappingDict.keys())[i]
        # get the existing IDs associated with this
        currentExistingIDs=mappingDict[currentHigherOrderCategory]
        # create a list of the same length as currentExistingIDs, containing the currentHigherOrderCategory repeated
        currentHigherOrderCategoryList=[currentHigherOrderCategory]*len(currentExistingIDs)
        # concatenate these to the output dataframe
        outDF=pd.concat([outDF,pd.DataFrame({'fieldValue':currentHigherOrderCategoryList,'itemIDs':currentExistingIDs})])
    
    # return the output dataframe
    return outDF
'''
def cosineDistanceMatrix(inputMatrixDF, axisToCompareWithin='columns',savePath=None, verbose=False):
    """
    This function takes in a matrix and computes the cosine distance metric for the elements of the specified axis.
    The results are returned as a square matrix with the rows and columns corresponding to the elements of the specified axis.
    
    The distance between elements i and j of the axisToCompareWithin is determined by the cosine distance of the vectors formed
    by all of the elements of the opposite axis.  

    Parameters
    ----------
    inputMatrixDF : pandas dataframe
        A matrix of some sort, which contains numeric values.  The column labels and row indexes should correspond to the
        identifiers of the elements of the specified axis.  They will be used to label the rows and columns of the output matrix.
    axisToCompareWithin : string
        Either 'rows' or 'columns', depending on whether you want to compute the cosine distance between the rows or the columns of the input matrix.
    savePath : string
        The path to which the results should be saved.  If None, then the results are not saved.  If '', then the results are saved to the current directory.
    verbose : boolean
        Whether to print out information about the progress of the function.
        
    Returns
    -------
    cosineDistanceMatrix : pandas dataframe
        A pandas dataframe with the cosine distance between each pair of elements of the specified axis.  The rows and columns correspond to the elements of the specified axis.
    
    """
    import pandas as pd
    import numpy as np
    import scipy.spatial.distance as ssd
    import os
    import h5py
    import timeit

    # check if the input matrix is a pandas dataframe and has informative row and column labels, which we will define as being strings
    # if it is, then proceed
    # if it isn't then raise an error explaning why a pandas dataframe is necessary (the column / row indexes need to be matched against the category dictionary))
    if not isinstance(inputMatrixDF,pd.DataFrame):
        raise ValueError('A pandas dataframe with informative row and column labels is required in order to compute the cosine distance between the rows or columns of the input matrix.')
    # check if the row and column labels are strings
    if not np.all([isinstance(x,str) for x in inputMatrixDF.index]) or not np.all([isinstance(x,str) for x in inputMatrixDF.columns]):
        raise ValueError('A pandas dataframe with informative row and column labels is required in order to compute the cosine distance between the rows or columns of the input matrix.')
    
    # go ahead and convert the input matrix to a numpy array
    inputMatrix=inputMatrixDF.values

    # parse the case logic for rows or columns
    if axisToCompareWithin=='rows':
        # use numpy.triu_indices to get the indexes of the upper triangle of the matrix,
        # which is the set of all unique comparisons between the rows
        comparisonIndexes=np.triu_indices(inputMatrix.shape[0],k=1)
        # initialize a list to store the results
        cosineDistanceResults=np.zeros(len(comparisonIndexes[0]))
        # loop through the comparison indexes and compute the cosine distance between the rows
        # print the number of comparisons being made
        if verbose:
            print('Computing cosine distance between '+str(len(comparisonIndexes[0]))+' rows...')
        for iComparison in range(len(comparisonIndexes)):
            # print the comparison being made, with the print statement replacing the previous one
            # get the current comparison indexes
            currentIndex1=comparisonIndexes[0][iComparison]
            currentIndex2=comparisonIndexes[1][iComparison]
            # if both are all zeros, then skip this comparison
            if np.all(inputMatrix[currentIndex1,:]==0) and np.all(inputMatrix[currentIndex2,:]==0):
                currentCosineDistance=np.nan
            else:
                if verbose:
                    print('\r'+'Computing cosine distance between row '+str(currentIndex1)+' and row '+str(currentIndex2)+'...',end='')

                # get the current comparison rows
                currentComparisonRow1=inputMatrix[currentIndex1,:]
                currentComparisonRow2=inputMatrix[currentIndex2,:]

                # find the nan values in either / both of the rows
                nanValues1=np.isnan(currentComparisonRow1)
                nanValues2=np.isnan(currentComparisonRow2)
                # combine these to get the indexes of the values that are not nan in either row
                nonNanValues=np.logical_not(np.logical_or(nanValues1,nanValues2))
                # get the non-nan values from each row
                currentComparisonRow1=currentComparisonRow1[nonNanValues]
                currentComparisonRow2=currentComparisonRow2[nonNanValues]
                # if there's anything left
                if len(currentComparisonRow1)>0:
                    # compute the cosine distance between the current comparison rows
                    # currentCosineDistance=ssd.cosine(currentComparisonRows[0,:],currentComparisonRows[1,:])
                    currentCosineDistance=fastNumbaCosinSimilarity(currentComparisonRow1,currentComparisonRow2)
                else:
                    # otherwise, set the cosine distance to nan
                    currentCosineDistance=np.nan
                # store the results
            cosineDistanceResults[iComparison]=currentCosineDistance

        # convert the results to a square matrix
        cosineDistanceMatrix=np.zeros((inputMatrix.shape[0],inputMatrix.shape[0]))
        # loop through the comparison indexes and store the results in the appropriate location in the square matrix
        for iComparison in range(len(comparisonIndexes)):
            # get the current comparison indexes
            currentComparisonIndexes=comparisonIndexes[iComparison]
            # get the current comparison rows
            # currentComparisonRows=inputMatrix[currentComparisonIndexes,:]
            # get the current cosine distance
            currentCosineDistance=cosineDistanceResults[iComparison]
            # store the results
            cosineDistanceMatrix[currentComparisonIndexes[0],currentComparisonIndexes[1]]=currentCosineDistance
            cosineDistanceMatrix[currentComparisonIndexes[1],currentComparisonIndexes[0]]=currentCosineDistance
        # set the row and column names
        rowNames=inputMatrixDF.index
        columnNames=inputMatrixDF.index
    elif axisToCompareWithin=='columns':

        # do the same thing as above, but with the columns
        # create a list of tuples, where each tuple contains the indexes of the columns to be compared
        # use numpy.triu_indices to get the indexes of the upper triangle of the matrix,
        # which is the set of all unique comparisons between the rows
        comparisonIndexes=np.triu_indices(inputMatrix.shape[1],k=1)
        # initialize a list to store the results
        cosineDistanceResults=np.zeros(len(comparisonIndexes[0]))
        # loop through the comparison indexes and compute the cosine distance between the columns
        for iComparison in range(len(comparisonIndexes)):
            currentIndex1=comparisonIndexes[0][iComparison]
            currentIndex2=comparisonIndexes[1][iComparison]
            if verbose:
                print('\r'+'Computing cosine distance between column '+str(currentIndex1)+' and column '+str(currentIndex2)+'...',end='')

            # get the current comparison rows
            currentComparisonColumn1=inputMatrix[currentIndex1,:]
            currentComparisonColumn2=inputMatrix[currentIndex2,:]
            # compute the cosine distance between the current comparison rows
            # currentCosineDistance=ssd.cosine(currentComparisonRows[0,:],currentComparisonRows[1,:])
            currentCosineDistance=fastNumbaCosinSimilarity(currentComparisonColumn1,currentComparisonColumn2)
            # store the results
            cosineDistanceResults[iComparison]=currentCosineDistance
        
        # convert the results to a square matrix of the size appropriate for axisToCompareWithin
        if axisToCompareWithin=='rows':
            cosineDistanceMatrix=np.zeros((inputMatrix.shape[0],inputMatrix.shape[0]))
        elif axisToCompareWithin=='columns':
            cosineDistanceMatrix=np.zeros((inputMatrix.shape[1],inputMatrix.shape[1]))
        # loop through the comparison indexes and store the results in the appropriate location in the square matrix
        for iComparison in range(len(comparisonIndexes)):
            # get the current comparison indexes
            currentIndex1=comparisonIndexes[0][iComparison]
            currentIndex2=comparisonIndexes[1][iComparison]
            # get the current comparison columns
            # currentComparisonColumns=inputMatrix[:,currentComparisonIndexes]
            # get the current cosine distance
            currentCosineDistance=cosineDistanceResults[iComparison]
            # store the results
            cosineDistanceMatrix[currentIndex1,currentIndex2]=currentCosineDistance
            cosineDistanceMatrix[currentIndex2,currentIndex1]=currentCosineDistance
        # set the row and column names
        rowNames=inputMatrixDF.columns
        columnNames=inputMatrixDF.columns
    
    # convert the results to a pandas dataframe
    cosineDistanceMatrix=pd.DataFrame(cosineDistanceMatrix,index=rowNames,columns=columnNames)
    return cosineDistanceMatrix
'''

'''
def fastNumbaCosinSimilarity(vec1,vec2):
    """
    The following is an implementation of cosine similarity that uses numba to speed up the computation.  From:
    https://medium.com/analytics-vidhya/speed-up-cosine-similarity-computations-in-python-using-numba-c04bc0741750
    
    """
    from numba import jit
    from numpy import ndarray
    from numpy import sqrt as npsqrt

    @jit(nopython=True)
    def cosine_similarity_numba(u:ndarray, v:ndarray):
        assert(u.shape[0] == v.shape[0])
        uv = 0
        uu = 0
        vv = 0
        for i in range(u.shape[0]):
            uv += u[i]*v[i]
            uu += u[i]*u[i]
            vv += v[i]*v[i]
        cos_theta = 1
        if uu!=0 and vv!=0:
            cos_theta = uv/npsqrt(uu*vv)
        return cos_theta
    
    return cosine_similarity_numba(vec1,vec2)
'''
from numba import jit
from numpy import ndarray
from numpy import sqrt as npsqrt

@jit(nopython=True)
def fastNumbaCosinSimilarity(u:ndarray, v:ndarray):
    assert(u.shape[0] == v.shape[0])
    uv = 0
    uu = 0
    vv = 0
    for i in range(u.shape[0]):
        uv += u[i]*v[i]
        uu += u[i]*u[i]
        vv += v[i]*v[i]
    cos_theta = 1
    if uu!=0 and vv!=0:
        cos_theta = uv/npsqrt(uu*vv)
    return cos_theta

# also we define a function which applies fastNumbaCosinSimilarity to a comparison of all rows or all columns of an input matrix, resulting in a square matrix of length equal to either the rows or the columns of the input matrix
@jit(nopython=True)
def cosineDistanceMatrix(inputMatrix:ndarray,axisToCompareWithin:str):
    """
    This function applies fastNumbaCosinSimilarity to a comparison of all rows or all columns of an input matrix, resulting in a square matrix of length equal to either the rows or the columns of the input matrix.
    
    Parameters
    ----------
    inputMatrix : ndarray
        An ndarray containing the rows or columns to be compared.
    axisToCompareWithin : string
        A string indicating whether the rows or the columns of the input matrix are to be compared.  Either 'rows' or 'columns'.

    
    """

    # parse the case logic for rows or columns
    if axisToCompareWithin=='rows':
        # use numpy.triu_indices to get the indexes of the upper triangle of the matrix,
        # which is the set of all unique comparisons between the rows
        comparisonIndexes=np.triu_indices(inputMatrix.shape[0],k=1)
    elif axisToCompareWithin=='columns':
        # use numpy.triu_indices to get the indexes of the upper triangle of the matrix,
        # which is the set of all unique comparisons between the columns
        comparisonIndexes=np.triu_indices(inputMatrix.shape[1],k=1)
    # initialize a list to store the results
    cosineDistanceResults=np.zeros(len(comparisonIndexes[0]))
        # loop through the comparison indexes and compute the cosine distance between the rows
    for iComparison in range(len(comparisonIndexes)):
        currentIndex1=comparisonIndexes[0][iComparison]
        currentIndex2=comparisonIndexes[1][iComparison]
        if axisToCompareWithin=='rows':
            currentComparisonRow1=inputMatrix[currentIndex1,:]
            currentComparisonRow2=inputMatrix[currentIndex2,:]
        elif axisToCompareWithin=='columns':
            currentComparisonRow1=inputMatrix[:,currentIndex1]
            currentComparisonRow2=inputMatrix[:,currentIndex2]

        # find the nan values in either / both of the rows
        nanValues1=np.isnan(currentComparisonRow1)
        nanValues2=np.isnan(currentComparisonRow2)
        # combine these to get the indexes of the values that are not nan in either row
        nonNanValues=np.logical_not(np.logical_or(nanValues1,nanValues2))
        # get the non-nan values from each row
        currentComparisonRow1=currentComparisonRow1[nonNanValues]
        currentComparisonRow2=currentComparisonRow2[nonNanValues]
        # do the same for 0 values
        zeroValues1=currentComparisonRow1==0
        zeroValues2=currentComparisonRow2==0
        # combine these to get the indexes of the values that are not 0 in both rows
        nonZeroValues=np.logical_not(np.logical_and(zeroValues1,zeroValues2))
        # get the non-zero values from each row
        currentComparisonRow1=currentComparisonRow1[nonZeroValues]
        currentComparisonRow2=currentComparisonRow2[nonZeroValues]

        # if there's anything left
        if len(currentComparisonRow1)>0:
            # compute the cosine distance between the current comparison rows
            # currentCosineDistance=ssd.cosine(currentComparisonRows[0,:],currentComparisonRows[1,:])
            currentCosineDistance=fastNumbaCosinSimilarity(currentComparisonRow1,currentComparisonRow2)
        else:
            # otherwise, set the cosine distance to nan
            currentCosineDistance=np.nan
        # store the results
    cosineDistanceResults[iComparison]=currentCosineDistance
    # convert the results to a square matrix
    if axisToCompareWithin=='rows':
        cosineDistanceMatrix=np.zeros((inputMatrix.shape[0],inputMatrix.shape[0]))
    elif axisToCompareWithin=='columns':
        cosineDistanceMatrix=np.zeros((inputMatrix.shape[1],inputMatrix.shape[1]))
    # loop through the comparison indexes and store the results in the appropriate location in the square matrix
    for iComparison in range(len(comparisonIndexes)):
        # get the current comparison indexes
        currentComparisonIndexes=comparisonIndexes[iComparison]
        # get the current comparison rows
        # currentComparisonRows=inputMatrix[currentComparisonIndexes,:]
        # get the current cosine distance
        currentCosineDistance=cosineDistanceResults[iComparison]
        # store the results
        cosineDistanceMatrix[currentComparisonIndexes[0],currentComparisonIndexes[1]]=currentCosineDistance
        cosineDistanceMatrix[currentComparisonIndexes[1],currentComparisonIndexes[0]]=currentCosineDistance




def fastSubsetDF_by_categoryKeyFile(inputDF,targetAxis,categoryKeyFile,categoryToExtract):
    """
    This function takes some of the tricks learned by implementing sumMergeMatrix_byCategories_REFACTOR 
    (e.g. pre-sorting and avoiding operating on pandas dataframes) and applies them to the task of extracting
    a subset of a pandas dataframe based on a category key file.  The category key file is either a pandas dataframe
    with target record IDs in the first column and category labels in the second column, or a dictionary with the
    category labels as keys and lists of target record IDs as lists of strings.  The function will return a pandas
    dataframe containing only the records corresponding to the target category label.

    Parameters
    ----------
    inputDF : pandas dataframe
        A pandas dataframe containing the records to be subsetted.
    targetAxis : string
        A string indicating whether the target records are in the rows or columns of the input dataframe.
        Either 'rows' or 'columns'.
    categoryKeyFile : pandas dataframe or dictionary
        A pandas dataframe or dictionary containing the category labels and corresponding record IDs.
    categoryToExtract : string
        A string indicating the category label to be extracted.

    Returns
    -------
    outputDF : pandas dataframe
        A pandas dataframe containing only the records corresponding to the target category label.
    """
    import pandas as pd
    import numpy as np
    import time
    # we begin taking a great deal of content from sumMergeMatrix_byCategories_REFACTOR 
    # and checking and parsing the input variables

    # check if the input matrix is a pandas dataframe
    # if it is, then proceed
    # if it isn't then raise an error explaning why a pandas dataframe is necessary (the column / row indexes need to be matched against the category dictionary))
    if not isinstance(inputDF,pd.DataFrame):
        raise ValueError('The input `inputDF` must be a pandas dataframe in order to match category indentities from `categoryKeyFile` with specific records in the matrix.')
    # go ahead and sort the input dataframe by the target axis
    # this will make it easier to extract the target records
    if targetAxis=='rows' or targetAxis==0 or targetAxis=='0':
        # sort the dataframe by the index
        inputDF=inputDF.sort_index(axis=0)
    elif targetAxis=='columns' or targetAxis==1 or targetAxis=='1':
        # sort the dataframe by the columns
        inputDF=inputDF.sort_index(axis=1)
    else:
        # print the current value of targetAxis
        print('The current value of `targetAxis` is: '+str(targetAxis))
        raise ValueError('The input `targetAxis` cannot be parsed.  Please enter either "rows" or "columns".')



    # parse the input category key file
    # if it's a dictionary, convert it to a pandas dataframe, as we'll be creating a boolean mask of the record ID vector / axis
    if isinstance(categoryKeyFile,dict):
        # convert the dictionary to a pandas dataframe
        # remember we want the record IDs to be the first column and the category labels to be the second column
        # go ahead and create an empty target dataframe
        categoryKeyFileDF=pd.DataFrame(columns=['itemID','fieldValue'])
        # loop through the dictionary to create a list of record IDs and a list of the associated category label repeated for the number of record IDs for the current key
        # the value associated with the key should already be a list
        for iKeys in range(len(categoryKeyFile.keys())):
            # get the current key
            currentKey=list(categoryKeyFile.keys())[iKeys]
            # get the current list of record IDs
            currentRecordIDs=categoryKeyFile[currentKey]
            # create a list of the current category label repeated for the number of record IDs
            currentCategoryLabels=currentKey * len(currentRecordIDs)
            # create a temporary dataframe for the current key
            currentKeyDF=pd.DataFrame({'itemID':currentRecordIDs,'fieldValue':currentCategoryLabels})
            # append the temporary dataframe to the target dataframe using concat
            categoryKeyFileDF=pd.concat([categoryKeyFileDF,currentKeyDF],axis=0,ignore_index=True)
    elif isinstance(categoryKeyFile,pd.DataFrame):
        # if the input category key file is already a pandas dataframe, then just set the categoryKeyFileDF variable to the input category key file
        categoryKeyFileDF=categoryKeyFile

    # go ahead and sort the categoryKeyFileDF by the recordID column, and then extract each column as a list (remember pandas is slow)
    categoryKeyFileDF=categoryKeyFileDF.sort_values(by='itemID')

    # for the sake of speed, we'll now extract the sorted itemIDs and fieldValues as lists
    itemIDList=list(categoryKeyFileDF['itemID'].values)
    fieldValueList=list(categoryKeyFileDF['fieldValue'].values)
    
    # NOTE:  one might think about trying to subset the categoryKeyFileDF now, so that we don't have to worry about working with records for categories we don't care about
    # HOWEVER we want the recordIDs to be of the same length as the designated axis of the input matrix so that we can use boolean masks / indexing.
    # this means that we need to do a check now to ensure that the labels of the target axis of inputDF are a subset of the 'recordIDs' in categoryKeyFileDF
    # if they aren't, then raise an error, if they are, then we subset the categoryKeyFileDF contents to only those records that are in the target axis of inputDF
    
    if targetAxis=='columns' or targetAxis==1 or targetAxis=='1':
        # get the target axis labels and treat them as a set
        targetAxisLabels=set(inputDF.columns)
        # get the record IDs from the categoryKeyFileDF and treat them as a set
        recordLabelsFromCategoryFile=set(itemIDList)
        # check if the target axis labels are a subset of the record labels
        if not targetAxisLabels.issubset(recordLabelsFromCategoryFile):
            # if they aren't, then raise an error
            raise ValueError('The target axis labels of the input matrix are not a subset of the record IDs in the categoryKeyFileDF.  This means that category assignments cannot be made for all records in the input matrix.')
        else:
            # if they are a subset, then we know that we have all of our records in the categoryKeyFileDF, but we may have more records than we need
            # such that the indexes of the inputDF are a subset of the recordIDs in the categoryKeyFileDF.
            # thus, in order to be able to use boolean masks, we need to subset the categoryKeyFileDF to only those records that are in the target axis of inputDF
            # we can do this by identifying the set difference between the targetAxisLabels and the recordLabelsFromCategoryFile
            # and then removing those records from the subset lists we created above
            # get the set difference between the targetAxisLabels and the recordLabelsFromCategoryFile
            setDifference=recordLabelsFromCategoryFile.difference(targetAxisLabels)
            # get the indexes of the set difference in a fast manner using numpy
            setDifferenceIndexes=np.where(np.isin(itemIDList,list(setDifference)))
            # create a temporary boolean vector mask that is of the appropriate length, with falses in the set difference indexes
            tempBooleanMask=np.ones(len(itemIDList),dtype=bool)
            tempBooleanMask[setDifferenceIndexes]=False
            # subset the itemIDList and fieldValueList to only those records that are in the target axis of inputDF

            # NOTE: after much testing the following observation is rendered:
            # indexing must be done of a like kind.  I.e. an array can only index an array, a list can only index a list, etc.
            curSubsetItemIDList=list(np.asarray(itemIDList)[tempBooleanMask])
            curSubsetFieldValueList=list(np.asarray(fieldValueList)[tempBooleanMask])
    elif targetAxis=='rows' or targetAxis==0 or targetAxis=='0':
        # get the target axis labels and treat them as a set
        targetAxisLabels=set(inputDF.index)
        # get the record IDs from the categoryKeyFileDF and treat them as a set
        recordLabelsFromCategoryFile=set(itemIDList)
        # check if the target axis labels are a subset of the record labels
        if not targetAxisLabels.issubset(recordLabelsFromCategoryFile):
            # if they aren't, then raise an error
            raise ValueError('The target axis labels of the input matrix are not a subset of the record IDs in the categoryKeyFileDF.  This means that category assignments cannot be made for all records in the input matrix.')
        else:
            # if they are a subset, then we know that we have all of our records in the categoryKeyFileDF, but we may have more records than we need
            # such that the indexes of the inputDF are a subset of the recordIDs in the categoryKeyFileDF.
            # thus, in order to be able to use boolean masks, we need to subset the categoryKeyFileDF to only those records that are in the target axis of inputDF
            # we can do this by identifying the set difference between the targetAxisLabels and the recordLabelsFromCategoryFile
            # and then removing those records from the subset lists we created above
            # get the set difference between the targetAxisLabels and the recordLabelsFromCategoryFile
            setDifference=recordLabelsFromCategoryFile.difference(targetAxisLabels)
            # get the indexes of the set difference in a fast manner using numpy
            setDifferenceIndexes=np.where(np.isin(itemIDList,list(setDifference)))
            # create a temporary boolean vector mask that is of the appropriate length, with falses in the set difference indexes
            tempBooleanMask=np.ones(len(itemIDList),dtype=bool)
            tempBooleanMask[setDifferenceIndexes]=False
            # subset the itemIDList and fieldValueList to only those records that are in the target axis of inputDF
            # NOTE: after much testing the following observation is rendered:
            # indexing must be done of a like kind.  I.e. an array can only index an array, a list can only index a list, etc.
            curSubsetItemIDList=list(np.asarray(itemIDList)[tempBooleanMask])
            curSubsetFieldValueList=list(np.asarray(fieldValueList)[tempBooleanMask])


    # in order for the boolean mask to work, the mask must be of the same length as the axis of the input matrix
    # as such check to ensure that the axis specified in targetAxis for the input matrix is of the same length as the number of records in the (post subset) categoryKeyFileDF

    # check to ensure that the axis specified in targetAxis for the input matrix is of the same length as the number of records in the categoryKeyFileDF
    # if it is, then proceed
    if targetAxis=='columns' or targetAxis==1 or targetAxis=='1':
        if len(inputDF.columns)!=len(curSubsetItemIDList):
            # print the lengths so the user can see what's going on
            print('The number of columns in the input matrix is ' + str(len(inputDF.columns)) + ' and the number of records in the categoryKeyFileDF is ' + str(len(curSubsetItemIDList)))
            raise ValueError('The number of columns in the input matrix does not match the number of records in the categoryKeyFileDF.  This is likely due to a mismatch in the axis specified in the targetAxis variable.')
    elif targetAxis=='rows' or targetAxis==0 or targetAxis=='0':
        if len(inputDF.index)!=len(curSubsetItemIDList):
            # print the lengths so the user can see what's going on
            print('The number of rows in the input matrix is ' + str(len(inputDF.index)) + ' and the number of records in the categoryKeyFileDF is ' + str(len(curSubsetItemIDList)))
            raise ValueError('The number of rows in the input matrix does not match the number of records in the categoryKeyFileDF.  This is likely due to a mismatch in the axis specified in the targetAxis variable.')


    # get the unique category labels from the categoryKeyFileDF
    uniqueCategoryLabels=list(set(curSubsetFieldValueList))

    # but also do a final check to see if categoryToExtract is actuall in the uniqueCategoryLabels
    if categoryToExtract not in uniqueCategoryLabels:
        # print the requested category to extract and the unique category labels
        print('The requested category to extract, ' + str(categoryToExtract) + ', is not in the unique category labels of the entities covered in the input dictionary: ' + str(uniqueCategoryLabels))
        print('This may be becaues the categoryToExtract is not represented in the input matrix.')
        print('Returnining an all zeros dataframe.')
        # return an all zeros dataframe
        return(pd.DataFrame(np.zeros(inputDF.shape),index=inputDF.index,columns=inputDF.columns))

    #print('Input variables have been checked and parsed, proceeding to indexer and intermediary array production.')    
    """
    Input variables have been checked and parsed, now we implement the subset-summation operation.
    """
    # print statment about precomputing and intermediary array production
    #print('Precomputing indexers and creating intermediary arrays.')

    # in sumMergeMatrix_byCategories_REFACTOR we created a dictionary of boolean masks, one for each category label, that could be used to subset the input matrix
    # however, here we are only doing this once, so we an just create the mask now
    # create the boolean mask for the requested category
    # create np.array of the categoryKeyFileDF['fieldValue'] (i.e. the category labels) content
    categoryLabelsArray=np.array(curSubsetFieldValueList)
    
    # generate bool vector corresponding to whether uniqueCategoryLabels == each element in categoryLabelsArray
    # do this in the fastest way possible, which is to use np.char.equal, which seems to be about 50 times faster than list comprehension
    # weirdly, we've also been getting a 'comparison of non-string arrays' error, so we'll check that both are string arrays
    # if categoryLabelsArray.dtype=='<U1' and np.asarray(uniqueCategoryLabels).dtype=='<U1':
    currentBoolMask=np.char.equal(np.asarray(categoryToExtract),categoryLabelsArray)
    #else:
    #    # print the dtypes and other info so the user can see what's going on
    #    print('The categoryLabelsArray.dtype is ' + str(categoryLabelsArray.dtype) + ' and the np.asarray(uniqueCategoryLabels).dtype is ' + str(np.asarray(uniqueCategoryLabels).dtype)) 
    #    print('The categoryLabelsArray is ' + str(categoryLabelsArray) + ' and the np.asarray(uniqueCategoryLabels) is ' + str(np.asarray(uniqueCategoryLabels)))
    #    raise ValueError('The categoryLabelsArray.dtype and the np.asarray(uniqueCategoryLabels).dtype are not both <U1.  This is likely due to a mismatch in the categoryToExtract variable and the categoryLabel variable in the categoryKeyFileDF.')

    # convert the content of the inputDF to a numpy array
    inputDFArray=inputDF.values

    # subset the inputDFArray using the currentBoolMask
    # this will be the intermediary array that we will use to generate the outputDF
    if targetAxis=='columns' or targetAxis==1 or targetAxis=='1':
        intermediaryArray=inputDFArray[:,currentBoolMask]
    elif targetAxis=='rows' or targetAxis==0 or targetAxis=='0':
        intermediaryArray=inputDFArray[currentBoolMask,:]

    # now produce the outputDF
    # the off axis will labels simply be the same as the inputDF
    # the on axis labels will be the subset of the categoryKeyFileDF['itemID'] that correspond to the currentBoolMask
    if targetAxis=='columns' or targetAxis==1 or targetAxis=='1':
        offAxisLabels=list(inputDF.index)
        onAxisLabels=list(np.asarray(curSubsetItemIDList)[currentBoolMask])
    elif targetAxis=='rows' or targetAxis==0 or targetAxis=='0':
        offAxisLabels=list(inputDF.columns)
        onAxisLabels=list(np.asarray(curSubsetItemIDList[currentBoolMask]))

    # create the outputDF
    if targetAxis=='columns' or targetAxis==1 or targetAxis=='1':
        outputDF=pd.DataFrame(intermediaryArray,columns=onAxisLabels,index=offAxisLabels)
    elif targetAxis=='rows' or targetAxis==0 or targetAxis=='0':
        outputDF=pd.DataFrame(intermediaryArray,columns=offAxisLabels,index=onAxisLabels)

    # save the output in accordance with the saveOutput variable
    return outputDF


def divideDFintoCategoryBasedSubsets(inputDF,categoryKeyFileDF,targetAxis='columns'):
    """
    The following function divides the inputDF into a dictionary of dataframes, one for each category in the categoryKeyFileDF.
    The keys of the output dictionary are the unique values of the categories assigned in categoryKeyFileDF.

    Parameters
    ----------
    inputDF : pandas dataframe
        The dataframe to be divided into category-based subsets.
    categoryKeyFileDF : pandas dataframe
        The dataframe containing the category keys for the inputDF.  It should be expected to have the following columns:
            itemID : string
                The unique identifier for each row of the inputDF.
            fieldValue : string
                The category label for each row of the inputDF.
    targetAxis : string
        The axis along which the subsets will be taken.  Must be either 'columns' or 'rows'.

    Returns
    -------
    outputDict : dictionary of pandas dataframes
        The dictionary of dataframes, one for each category in the categoryKeyFileDF.    
    """

    # get the unique category labels from categoryKeyFileDF
    uniqueCategoryLabels=list(categoryKeyFileDF['fieldValue'].unique())

    # create the output dictionary
    outputDict={}
    # iterate through the unique category labels
    for curCategoryLabel in uniqueCategoryLabels:
        # use fastSubsetDF_by_categoryKeyFile(inputDF,targetAxis,categoryKeyFile,categoryToExtract) to subset the inputDF
        currentSubsetDF=fastSubsetDF_by_categoryKeyFile(inputDF,targetAxis,categoryKeyFileDF,curCategoryLabel)
        # add the currentSubsetDF to the outputDict
        outputDict[curCategoryLabel]=currentSubsetDF

    # return the outputDict
    return outputDict





    



def tupleDictFromDictFields(inputStructs,targetField,nameField='infer'):
    '''
    This function creates a tuple dictionary, as produced by applyRegexsToDirOfXML, wherein the keys are the tuples corresponding to the identifiers 
    off the inputStructs and the unique values of the target field.  Thus this function assumes that the range of unique values for targetField is 
    reasonably finite, and can produce a matrix-like storage structure wherein the colums correspond to the input identifiers, and the (substantially smaller number)
    of rows correspond to the unique values of the target field.  Violation of the assumption that len(uniqueValues(targetField)) << len(inputStructs) will result in
    a very inefficient storage structure.

    Parameters
    ----------
    inputStructs : list of dictionaries
        A list of valid objects (file paths, xml strings, or dictionary objects) to be searched.
    targetField : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
    nameField : string, optional
        A string corresponding to the field, presumed to be present in all input structures, to be used as the identifier for the input structures.  The default is 'infer', which will attempt to infer the name field from the input structures using the detectDataSourceFromSchema to determine which of the currently accepted schemas the input structures conform to.

    Returns
    -------
    tupleDict: dictionary
        A dictionary with tuples as keys and booleans as values, indicating whether the targetField was found in the inputStructs.

    See Also
    --------
    applyRegexsToDirOfXML : Searches a directory of XML files for the presence of a string phrase.  Returns a tuple dictionary.
    convertTupleDictToEfficientDict : Converts a tuple dictionary to a more efficient dictionary structure.
    '''
    import xmltodict
    import os
    import copy
    from warnings import warn

    # first detect what kind of data source we are dealing with by looking at the first item in the inputStructs
    testInput=inputStructs[0]
    # if it's a string then test if it's a file path
    if isinstance(testInput,str):
        # if it's a file path then test if it's a valid file path
        if os.path.isfile(testInput):
            # if it's a valid file path then test if it's an XML file
            if testInput.endswith('.xml'):
                # if it's an XML file then read it in as a dictionary
                inputType='xmlFile'
                # take this opportunity to parse the nameField='infer' logic
                if nameField=='infer':
                    detectedDataSource=detectDataSourceFromSchema(testInput)
                    if detectedDataSource == 'NSF':
                        nameField=['rootTag','Award','AwardID']
                    elif detectedDataSource == 'NIH':
                        nameField=['rootTag','APPLICATION_ID']
                    elif detectedDataSource == 'grantsGov':
                        nameField=['rootTag','OpportunityID']
                    else:
                        raise ValueError('"infer" option for nameField using detectDataSourceFromSchema function returned unrecognized data source.')
                # if the nameField option is not set to "infer" then just use the the filenames, but the actual processing of this will be handled later
                elif not nameField=='' or nameField==None:
                    nameField=nameField
                else:
                    nameField='fileName'

            else:
                # if it's not an XML file then raise an error
                raise ValueError('The inputStructs variable contains a file-like string with "xml" extension that is not a valid file path.')
        # if it's a string but not a file, check if it's a valid XML string
        elif testInput.startswith('<?xml version="1.0" encoding="UTF-8"?>'):
            inputType='xmlString'
        # TODO: maybe also consider checking if it's a valid JSON string
    # if it's not a string then check if it's a dictionary
    elif isinstance(testInput,dict):
        inputType='dict'
    # if it's not a string or a dictionary then raise an error
    else:
        raise ValueError('The inputStructs variable contains an item that is not a valid file path, XML string, or dictionary.')
    
    # establish the tuple dictionary
    tupleDict={}

    # TODO consider throwing an error if the wrong combination of inputType and nameField is used
    # now iterate across the inputStructs and extract the targetField and nameField and store them in a tuple dictionary
    for iInput in inputStructs:
        # handle the input appropriately

        # wrap it in a try except in case there's a problem loading the file
        try:
            if inputType=='xmlFile':
                # read in the input as a dictionary
                with open(iInput) as fd:
                    inputDict = xmltodict.parse(fd.read())
                # close the file
                fd.close()
            elif inputType=='xmlString':
                # read in the input as a dictionary
                inputDict = xmltodict.parse(iInput)
            elif inputType=='dict':
                # copy the inputDict to a new variable
                inputDict=copy.deepcopy(iInput)
            else:
                raise ValueError('The inputStructs variable contains an item that is not a valid file path, XML string, or dictionary.')
            # extract the targetField and nameField
            iTargetField= extractValueFromDictField(inputDict,targetField)
            # TODO:  there is currently no handling for case 'fileName'
            iNameField=extractValueFromDictField(inputDict,nameField)
            tupleDict[(iTargetField,iNameField,)]=True
        except:
            warn('There was a problem loading the file: '+iInput)
            tupleDict[(iTargetField,iNameField,)]=False

        

    # return the tuple dictionary
    return tupleDict

def extractValueFromDictField(inputDict,fieldList):
    """
    This function extracts the value from a nested dictionary field.

    Parameters
    ----------
    inputDict : dictionary
        A dictionary containing the nested field to be extracted.
    fieldList : list of strings
        A list of strings corresponding to the nested fields to be extracted.
        
    Returns
    -------
    fieldValue : string
        A string corresponding to the value of the nested field.   
    """
    # iterate across the fieldList to get the nested field
    for iField in fieldList:
        try:
            inputDict=inputDict[iField]
        except:
            # throw an error indicating which file failed
            raise ValueError('Field ' + str(iField) + ' not found in dictionary ' + str(inputDict) + '. \n Input list = ' + str(fieldList)) 
    # extract the targetField
    fieldValue=inputDict
    # return the targetField
    return fieldValue

def searchInputListsForKeywords(inputLists,keywordList):
    """
    Divides up the items in the inputLists--for items whose description includes
    an item from the input keywordList variable--into groups associated by keyword.

    Returns a dictionary wherein the keys are keywords and the values are lists of items
    wherein the the keyword was found in the associated description.

    Parameters
    ----------
    inputLists : list of lists
        A list of lists wherein each list contains a set of items to be assessed for keyword occurrences. 
    keywordList : list of strings
        A list of strings corresponding to the keywords one is interested in assessing the occurrences of. 

    Returns
    -------
    grantFindsOut : dictionary
        A a dictionary wherein the keys are keywords and the values are N long boolean vectors indicating
    whether the keyword was found in the associated description.

    See Also
    --------
    grants_by_Agencies : Divides up the grant IDs ('OpportunityID') from the input grantsDF by top level agency.
    """
    import pandas as pd
    import re
    import time
    import numpy as np
    # if inputLists is a series, then convert it to a list
    if type(inputLists)==pd.core.series.Series:
        inputLists=inputLists.values.tolist()

    # create a dictionary in which each each key is a keyword, and the value is a blank boolean vector of length N, where N is the number of items in the inputLists
    # first create a blank boolean vector of length N that will be placed in all dictionary entries
    blankBoolVec=[False]*len(inputLists)
    # then create the dictionary itself
    grantFindsOut={}
    # then populate the dictionary with the blank boolean vectors
    for iKeywords in keywordList:
        grantFindsOut[iKeywords]=blankBoolVec
    # next we compile all of the regex searches that we will perform
    # we replace dashes with spaces to be insensitive to variations in hyphenation behaviors
    compiledRegexList=[re.compile('\\b'+iKeywords.lower().replace('-',' ')+'\\b') for iKeywords in keywordList]

    # next define the function that will be used to search the input text for the compiled regex
    # we do this so that we can parallelize the search
    def searchInputForCompiledRegex(inputText,compiledRegex):
        """
        Searches the input text for the compiled regex and returns True if found, False if not found.
        Function is used to parallelize the search for keywords in the input text.
        """
        # case insensitive find for the keyword phrase
        # use try except to handle the case where there is no description field
        try:
        # get rid of dashes to be insensitive to variations in hyphenation behaviors
            if bool(compiledRegex.search(inputText.lower().replace('-',' '))):
                    #append the ID if found
                    return True
            else:
                return False
        except:
            # do nothing, if there's no description field, then the word can't be found
            return False

    # next we iterate across the keywords and compiled regexes and search the inputLists for the keywords
    for iKeywords,iCompiledSearch in zip(keywordList,compiledRegexList):
        for iRows,iListing in enumerate(inputLists):
            # case insensitive find for the keyword phrase
            # use try except to handle the case where there is no description field
            try:
                # get rid of dashes to be insensitive to variations in hyphenation behaviors
                if bool(iCompiledSearch.search(iListing.lower().replace('-',' '))):
                    #append the ID if found
                    grantFindsOut[iKeywords][iRows]=True
            except:
                # do nothing, if there's no description field, then the word can't be found and the false remains in place
                pass
    return grantFindsOut

def applyRegexToInput(inputText,stringPhrase):
    """
    Applies a regex search to the inputText and returns a boolean indicating whether the stringPhrase was found.

    NOTE: case sensitive is depricated.

    Parameters
    ----------
    inputText : string
        A string to be assessed for the presence of the stringPhrase.
    stringPhrase : string
        A string corresponding to the phrase one is interested in assessing the occurrences of. 

    Returns
    -------
    bool
        A boolean indicating whether the stringPhrase was found in the inputText.
    """
    import re

    compiledSearch=re.compile(stringPhrase)
    try:
        if bool(compiledSearch.search(inputText)):
            return True
        else:
            return False
    except:
        return False

def applyRegexToXMLFile(xmlFilePath,stringPhrase,fieldsSelect):
    """
    Applies a regex search to the inputText and returns a boolean indicating whether the stringPhrase was found.
    
    NOTE: case sensitive is depricated.

    Parameters
    ----------
    xmlFilePath : string
        A string corresponding to the path to the xml file to be searched.  Can also be the file contents as a string.
    stringPhrase : string
        A string corresponding to the phrase one is interested in assessing the occurrences of.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.

    DEPRICATION NOTE: This function has been depricated by applyRegexesToText and is no longer used by the current version of applyRegexsToDirOfXML
    Why?  Because this version is terribly inefficient.  It loads the relevant XML file into memory *each time* a regex is applied.  This is in addition to
    the overhead incurred by lemmatizing the text each time a regex is performed.  The new version loads the XML file once, prepares it once, and then applies the regexes iteratively.    
    
    Returns
    -------
    bool
        A boolean indicating whether the stringPhrase was found in the inputText.
    """
    import xmltodict
    import re
    from warnings import warn

    # print a 

    # wrap the whole thing in a try except to handle the case where the xml file is empty or malformed
    try:

        # if the xmlFilePath is a string, then assume it's the file path and load the file
        if type(xmlFilePath)==str:
            with open(xmlFilePath) as f:
                xmlDict=xmltodict.parse(f.read())
        # close the file
            f.close()
        else:
            xmlDict=xmltodict.parse(xmlFilePath)
        # use extractValueFromDictField to extract the relevant field
        targetRegexText=extractValueFromDictField(xmlDict,fieldsSelect)

        # if xmlDict is empty, just go ahead and return False
        if targetRegexText==None:
            # print a warning
            print('WARNING: targetRegexText is None')
            return False
        # otherwise, check if it's empty
        # NOTE: for a while this was set up wrong and was triggering on any length greater than zero
        elif len(targetRegexText)==0:
            # print a warning
            print('WARNING: targetRegexText is empty')
            return False
        # otherwise proceed with the search
        
        # now that we have the relevant content, we need to convert the text to nlp-ready text
        # use prepareTextForNLP(inputText,stopwordsList=None,lemmatizer=None)
        targetRegexText=prepareTextForNLP(targetRegexText)
    
        stringPhrase=prepareTextForNLP(stringPhrase)

        # use applyRegexToInput
        outputBool=applyRegexToInput(targetRegexText,stringPhrase)
    except:
        warn('WARNING: applyRegexToXMLFile failed for file ' + str(xmlFilePath))
        outputBool=False

    return outputBool

def applyRegexesToFieldFromXMLFile(xmlFilePath,regexList,fieldsSelect):
    """
    This function is a wrapper around applyRegexesToText, which loads *a specific field* from an XML file and applies a list of regexes to it.
    This function is designed to be used with applyRegexesToDirOfXML, which will iterate across a directory of XML files and apply a list of regexes to each file.
    The regex search terms are prepared *outside* of this function, so that they only need to be compiled once.

    Parameters
    ----------
    xmlFilePath : string
        A string corresponding to the path to the xml file to be searched.  Can also be the file contents as a string.
    regexList : list of strings
        A list of *PRECOMPILED* regexes to be searched for in the inputText.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.

    Returns
    -------
    boolVec : list of booleans
        A list of booleans indicating whether each regex was found in the string.
    """
    # we will make use of either ElementTree from xml.etree, lxml.etree, or xmltodict
    # remember, we are only loading a specific field from the XML file, so we don't want to load the whole thing, in order to avoid read/write overhead
    # we will use the xmltodict library, which is a wrapper around ElementTree, but is much easier to use
    import xmltodict
    import xml.etree.ElementTree as ET
    import re
    from warnings import warn
    
    # if it's a string we can assume it's a file path to an xml file
    if type(xmlFilePath)==str:
        # without loading the whole file, we can begin to parse the nodes
        # first we need to get the root node
        # we will use the xmltodict library, which is a wrapper around ElementTree, but is much easier to use
        # wrap the load attempt in a try except to handle the case where the xml file is empty or malformed
        try:
            with open(xmlFilePath) as f:
                # NOTE: copilot is being stubborn, and seems to want to go ahead and load the whole file
                # maybe there isn't a way to merely parse the xml structure without loading the whole thing?
                # potentially relevant stack overflow: https://stackoverflow.com/questions/324214/what-is-the-fastest-way-to-parse-large-xml-docs-in-python?rq=4
                # NOTE: this is a problem, because it means that we are loading the whole file, which is very inefficient
                XMLfileContents=f.read()
                xmlDict=xmltodict.parse(XMLfileContents)
            # close the file
            f.close()
        except:
            warn('WARNING: applyRegexesToFieldFromXMLFile failed for file ' + str(xmlFilePath) + '.\nReturning vector of False values, indicating failure to find terms.')
            return [False]*len(regexList)
    elif type(xmlFilePath)==dict:
        xmlDict=xmlFilePath
    else:
        raise TypeError('The xmlFilePath must be either a string or a dictionary.')
    
    # use extractValueFromDictField(xmlDict,fieldsSelect) to extract the relevant field, but wrap in try except
    # first, if xmlDict is empty, just go ahead and return False
    if len(xmlDict.keys())==0:
        # print a warning
        print('WARNING: xmlDict is empty')
        return [False]*len(regexList)
    try:
        targetRegexText=extractValueFromDictField(xmlDict,fieldsSelect)
    except:
        # there are several reasons this could fail, let's try responding to each of them
        # first and most likely is that fieldsSelect is not a list such that each element is a string
        # so check that it is a list and that all elements are strings
        if type(fieldsSelect)==list:
            # check that all elements are strings
            if not all([type(iField)==str for iField in fieldsSelect]): 
                # if not, then raise an error
                raise TypeError('The fieldsSelect variable must be a list of strings, with each string corresponding to sequentially nested dictionary / xml fields.')
            else:
                # if it is a list, and all elements are strings, then this probably isn't your issue
                pass
        else:
            # if it's not a list, then raise an error
            raise TypeError('The fieldsSelect variable must be a list of strings, with each string corresponding to sequentially nested dictionary / xml fields.')
        # next there could be a mismatch between the expected fields of fieldsSelect and the actual fields of the xmlDict
        # so try and walk through the fieldsSelect and see if they are sequentially present in the xmlDict
        for iField in fieldsSelect:
            # check if the field is present in the xmlDict
            if iField in list(xmlDict.keys()):
                # if it is, then update the xmlDict
                xmlDict=xmlDict[iField]
            else:
                # if it's not, then raise an error indicating how deep the mismatch was found, and what the current values were
                # first find the depth of iField in fieldsSelect
                iFieldDepth=fieldsSelect.index(iField)
                raise ValueError('Mismatch between fieldsSelect and xmlDict.keys() found at depth ' + str(iFieldDepth) + '.\n' + iField + ' of fieldsSelect = ' + str(fieldsSelect) + '\n whereas xmlDict.keys() = ' + str(list(xmlDict.keys())))
        # that's a reasonable attempt at forseeing errors, if it's not one of these throw a generic error
        else:
            raise ValueError('applyRegexesToFieldFromXMLFile failed for file ' + str(xmlFilePath))


    # now that we have the relevant content, we need to convert the text to nlp-ready text
    # wrap this in a try except to handle the case where the text is empty or malformed
    try:
        NLPreadyText=prepareTextForNLP(targetRegexText)
    except:
        # well we should expect targetRegexText to be a string, so if it's not, then raise an error
        # if it's None type, potentially indicating an empty field, then simply return a vector of False values
        if targetRegexText==None:
            warn('The targetRegexText variable is None type, indicating an empty field. Returning vector of False values, indicating failure to find terms.')
            return [False]*len(regexList)
        elif type(targetRegexText)!=str:
            warn('The targetRegexText variable must be a string. Instead it is of type ' + str(type(targetRegexText)) + ' for file ' + str(xmlFilePath) + '\n returning vector of False values, indicating failure to find terms.')
        else :
            warn('WARNING: applyRegexesToFieldFromXMLFile failed for file ' + str(xmlFilePath) + '.\nReturning vector of False values, indicating failure to find terms. + \n' + str(targetRegexText))
    # now we can iterate across the regexList and apply each regex to the NLPreadyText
    # use applyRegexesToText(NLPreadyText,regexList)
    boolVec=applyRegexesToText(NLPreadyText,regexList)
    # return the boolVec
    return boolVec
    

  


def applyRegexesToText(inputText,regexList):
    """
    This function applies a list of regexes to a string and returns a boolean vector indicating whether each regex was found in the string.

    Parameters
    ----------
    inputText : string
        The string to be searched.
    regexList : list of strings
        A list of *PRECOMPILED* regexes to be searched for in the inputText.

    Returns
    -------
    boolVec : list of booleans
        A list of booleans indicating whether each regex was found in the string.
    """
    import re

    # initialize a vector of booleans (False)
    boolVec=[False]*len(regexList)

    # prepare the input text for NLP
    inputText=prepareTextForNLP(inputText)
    # prepare the search phrases for NLP using list comprehension
    # NOTE: we do not want to do this here, because we don't want to do it each time the function is called
    # regexList=[prepareTextForNLP(iRegex) for iRegex in regexList]

    # compile the regexes
    # NOTE: Similarly, we don't want to do this here, because we don't want to do it each time the function is called
    # compiledRegexList=[re.compile(iRegex) for iRegex in regexList]

    # iterate across the regexes and search for them in the input text
    for iRegex in range(len(regexList)):
        # search for the regex in the input text using re.search
        searchResults=re.search(regexList[iRegex],inputText)
        # if the regex was found, then update the boolVec
        if searchResults:
            boolVec[iRegex]=True
        else:
            # if the regex was not found, then do nothing, because the boolVec is already initialized to False
            pass

    return boolVec


    

def prepareTextForNLP(inputText,stopwordsList=None,lemmatizer=None):
    """
    This function is designed to take a string of text and prepare it for NLP analysis.  It does this by:
        1) converting to lowercase
        1.5) replacing dashes with spaces
        2) removing punctuation
        3) removing stopwords
        4) removing digits
        5) removing whitespace
        6) removing single character words
        7) lemmatizing
    Inputs:
        inputText: string
            The text to be prepared for NLP analysis
    Outputs:
        outputText: string
            The text prepared for NLP analysis
    """
    import re
    import nltk
    # download the stopwords and wordnet corpora if they haven't already been downloaded
    # do not do this in something that is called this frequently
    # nltk.download('stopwords',quiet=True)
    # nltk.download('wordnet',quiet=True)
    # import the necessary libraries
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    # convert to lowercase
    outputText=inputText.lower()
    # replace dashes with spaces
    outputText=re.sub(r'-',' ',outputText)
    # remove punctuation
    outputText=re.sub(r'[^\w\s]','',outputText)
    # remove stopwords
    if stopwordsList == None:
        stop_words = set(stopwords.words('english'))
    elif not stopwordsList == '':
        stop_words = set(stopwordsList)
    else:
        stop_words = set() # the empty set
    outputText = ' '.join([word for word in outputText.split() if word not in stop_words])
    # remove digits
    outputText=re.sub(r'\d+','',outputText)
    # remove whitespace
    outputText=re.sub(r'\s+',' ',outputText)
    # remove single character words
    outputText=re.sub(r'\b[a-zA-Z]\b','',outputText)
    # lemmatize
    if lemmatizer is None:
        lemmatizer = WordNetLemmatizer()
    else:
        lemmatizer=lemmatizer
    outputText=' '.join([lemmatizer.lemmatize(word) for word in outputText.split()])
    return outputText

def prepareAllTextsForNLP(inputTexts,stopwordsList=None,lemmatizer=None):
    """
    This function is designed to take a list of strings of text and prepare them for NLP analysis.  It does this by:
        1) converting to lowercase
        1.5) replacing dashes with spaces
        2) removing punctuation
        3) removing stopwords
        4) removing digits
        5) removing whitespace
        6) removing single character words
        7) lemmatizing
    
    Also, it is optinally possible to run this function in a parralized fashion, if dask is installed.
    
    Inputs:
        inputTexts: list of strings
            The texts to be prepared for NLP analysis
        stopwordsList: list of strings
            A list of stopwords to be removed from the text
        lemmatizer: nltk.stem.WordNetLemmatizer
            A lemmatizer to be used to lemmatize the text
    Outputs:
        outputTexts: list of strings
            The texts prepared for NLP analysis
    """
    outputTexts=[]
    for iText in inputTexts:
        outputTexts.append(prepareTextForNLP(iText,stopwordsList=stopwordsList,lemmatizer=lemmatizer))
    return outputTexts

def detectDataSourceFromSchema(testDirOrFile):
    """
    This function is designed to detect the data source of a given file or directory based on the schema of the file(s).
    Inputs:
        testDirOrFile: string
            A string corresponding to the path to the file or directory to be tested
    Outputs:
        dataSource: string
            A string corresponding to the data source of the file or directory.  Currently either "NSF" or "grantsGov"
    """
    import os
    import xmltodict
    import json

    # parametrs to set:
    # minFieldThreshold: int
    #  The minimum number of fields that must match known fields for the corresponding schema in order for it to be considerd a valid mathc
    minFieldThreshold=3
    # A list of fields found in the NSF schema
    NSFfields=['AwardID','AbstractNarration','AwardTitle','AwardAmount','NSF_ID','Directorate']
    # A list of fields found in the grants.gov schema
    grantsGovFields=['OpportunityID','Synopsis','Title','EstimatedTotalProgramFunding','AgencyCode','Description']
    # a list of fields found in the NIH schema; all caps, because YELLING
    NIHfields=['APPLICATION_ID', 'ACTIVITY', 'ADMINISTERING_IC', 'APPLICATION_TYPE', 'ARRA_FUNDED', 'AWARD_NOTICE_DATE', 'BUDGET_START', 'BUDGET_END', 'CFDA_CODE', 'CORE_PROJECT_NUM', 'ED_INST_TYPE']

    # for a detailed overview of the NSF grant award data schema view:
    # https://github.com/macks22/nsf-award-data/blob/master/docs/nsf-xml-schema-details.md#xml-schema-breakdown
    # the schema itself can be downloaded from here:
    # https://www.nsf.gov/awardsearch/resources/Award.xsd

    # for a detailed overview of the grants.gov grant award data schema view:
    # http://apply.grants.gov/system/OpportunityDetail-V1.0
    # the schema itself can be downloaded from here:
    # https://apply07.grants.gov/apply/system/schemas/OpportunityDetail-V1.0.xsd
    # determine if input is file or directory
    # first check if it's a string
    if type(testDirOrFile)==str:
        # if it's a string, then check if it's a directory
        if os.path.isdir(testDirOrFile):
            # if it's a directory, then simply pick the first xml file in the directory
            testFile=os.listdir(testDirOrFile)[0]
            with open(testFile) as f:
                xmlDict=xmltodict.parse(f.read())
            f.close()
        # if it's a file, then simply use that file
        elif os.path.isfile(testDirOrFile):
            testFile=testDirOrFile
            with open(testFile) as f:
                xmlDict=xmltodict.parse(f.read())
            f.close()
        else:
            # if it's a string, but neither of the above, then try and parse it as xml or json
            try:
                xmlDict=xmltodict.parse(testDirOrFile)
            except:
                try:
                    xmlDict=json.loads(testDirOrFile)
                except:
                    print('Error: input is a string but is not a valid file, directory, xml, or json')
                    return None
    # if it's a dictionary, then assume it's already been parsed
    elif type(testDirOrFile)==dict:
        xmlDict=testDirOrFile
    # otherwise, return an error
    else:
        print('Error: input of type '+str(type(testDirOrFile))+' is not a valid file, directory, xml, json, or dict')
        return None
    # read in the presumptive xml file using xmltodict
    # hopefully it is validly structured and we don't need to use beautiful soup to fix it

    # close the file

    # now check it for the relevant fields
    # recurisvely search the xmlDict for all keys, including exhaustive search of nested dictionaries
    def getKeys(inputDict):
        keys=[]
        for key in inputDict.keys():
            keys.append(key)
            if type(inputDict[key])==dict:
                keys.extend(getKeys(inputDict[key]))
        return keys
    allKeys=getKeys(xmlDict)

    # now check if the NSF fields are present
    # NOTE: add checks for other data schemas here as additonal data sources are added
    NSFfieldCount=0
    for NSFfield in NSFfields:
        if NSFfield in allKeys:
            NSFfieldCount+=1
    # now check if the grants.gov fields are present
    grantsGovFieldCount=0
    for grantsGovField in grantsGovFields:
        if grantsGovField in allKeys:
            grantsGovFieldCount+=1
    # now check if the NIH fields are present
    NIHfieldCount=0
    for NIHfield in NIHfields:
        if NIHfield in allKeys:
            NIHfieldCount+=1

    # now determine which data source is the best match
    # heaven help you if the sequencing of these matters
    if NSFfieldCount>=minFieldThreshold:
        dataSource='NSF'
    elif grantsGovFieldCount>=minFieldThreshold:
        dataSource='grantsGov'
    elif NIHfieldCount>=minFieldThreshold:
        dataSource='NIH'
    else:    
        dataSource=None
    return dataSource

def detectCommunitiesFromMatrix(inputMatrixOrDF,method='louvain',parameterSweep=True,methodParams=None):
    """
    This function takes in a matrix and performs community detection on the connectivity graph represented by that matrix.
    Can handle either a numpy matrix or a pandas dataframe. Uses networkx to perform the community detection.

    Inputs:
        inputMatrixOrDF: numpy matrix or pandas dataframe
            The matrix to be analyzed for community structure
        method: string
            The method to be used for community detection.  Currently only 'louvain' is supported.
        parameterSweep: boolean
            Whether or not to perform a paramter sweep and return the consensus community assignments from this process.
            If false, then the methodParams are used to perform a single community detection.
            If true, then any methodParams key value pairing with a list as a value will be swept over.  Multiple list paramter values will be swept in a combinatorial fashion.  Any methodParams key value pairing with a single value will be used for all parameter sweeps.
            Results will be the consensus community assignments from all parameter sweeps.
        methodParams: dictionary
            A dictionary containing the parameters to be used for community detection.  If parameterSweep is true, then any methodParams key value pairing with a list as a value will be swept over.  Multiple list paramter values will be swept in a combinatorial fashion.  Any methodParams key value pairing with a single value will be used for all parameter sweeps.
            Parameters should be specific to the method being used.

    Outputs:
        communities: dictionary
            A dictionary containing the community assignments for each node in the graph

    Testing:
    import pandas as pd
    import numpy as np
    pathToTestInput='/media/dan/HD4/coding/gitDir/USG_grants_crawl/inputData/NSF/analyzed/coOccurrenceMatrix.csv'
    inputMatrixOrDF=pd.read_csv(pathToTestInput,index_col=0,header=0)
    # test the new consensus method
    threshold=.05
    consensuPartitionOut=consensus_partition(inputMatrixOrDF.values, threshold, num_reps=100, random_seed=None)
    # to test the parameter sweep functionality, we'll test a range of resolution values for the louvain method
    # we'll test 10 random seeds along with 20 total resolution values (10 above and 10 below the default value of 1)
    # so create the methodParams for this
    parameterSweep=True
    method='louvain'
    methodParams={'resolution': (list(np.logspace(0,.1,100))+ list(np.logspace(0,-.15,100))),'seed':[None for x in range(2)]}
    testCommunities=detectCommunitiesFromMatrix(inputMatrixOrDF,method=method,parameterSweep=parameterSweep,methodParams=methodParams)
    # just for the sake of transparency, lets compute the number of communities for each of the sweep runs
    communityCounts=[len(x)for x in testCommunities]
    agreementMatrix=agreementMatrixFromCommunityAssignments(testCommunities)

    """
    import networkx as nx
    import numpy as np
    import pandas as pd
    import itertools
    from tqdm import tqdm

    # first check if the input is a matrix or a dataframe
    if type(inputMatrixOrDF)==np.ndarray:
        # if it's an np array it's fine
        workingMatrix=inputMatrixOrDF
        # now check that it's square
        if workingMatrix.shape[0]!=workingMatrix.shape[1]:
            # throw a value error if it's not square, and report the shape
            raise ValueError('Input matrix is not square.  Shape is '+str(workingMatrix.shape))
        # otherwise convert the nparray to a networkx graph
        workingGraph=nx.from_numpy_array(workingMatrix)
    # if it's a np matrix make the same conversion
    elif type(inputMatrixOrDF)==np.matrix:
        workingMatrix=inputMatrixOrDF
        if workingMatrix.shape[0]!=workingMatrix.shape[1]:
            raise ValueError('Input matrix is not square.  Shape is '+str(workingMatrix.shape))
        workingGraph=nx.from_numpy_matrix(workingMatrix)
    # in the case of 
    elif type(inputMatrixOrDF)==pd.DataFrame:
        # if it's a dataframe, convert it to an array
        workingMatrix=inputMatrixOrDF.values
        # now check that it's square
        if workingMatrix.shape[0]!=workingMatrix.shape[1]:
            # throw a value error if it's not square, and report the shape
            raise ValueError('Input matrix is not square.  Shape is '+str(workingMatrix.shape))
        # otherwise convert the nparray to a networkx graph
        workingGraph=nx.from_numpy_array(workingMatrix)
    # Also, if it's already a networkx graph, you're fine
    elif type(inputMatrixOrDF)==nx.classes.graph.Graph:
        workingGraph=inputMatrixOrDF
    else:
        # raise a type error if it's not one of the above, indicate type and shape of input
        raise TypeError('Input must be a numpy matrix, numpy array, pandas dataframe, or networkx graph.\n  Type is '+str(type(inputMatrixOrDF))+' and shape is '+str(inputMatrixOrDF.shape))

    """
    Here we parse the parameterSweep input and create a list of dictionaries to be used for the parameter sweep.
    
    """

    if parameterSweep==True:
            # if parameterSweep is true, then sweep over the parameters
            # first, get the keys and values from the methodParams
            methodParamKeys=list(methodParams.keys())
            methodParamValues=list(methodParams.values())
            # now check if any of the values are lists
            # if they are, then create a dictionary of all possible combinations singleton values from the lists, along with the non-sweep parameters.
            # if they are not, then there will only be one dictionary in the list
            # create the holder for the dictionaries
            methodParamDicts=[]
            # create a dummy dictionary that will be used as the template for the elements of methodParamDicts
            # it should contain all non sweep parameters, with non sweep parameters keys being paired with a placeholder None
            dummyDict={}
            for iKey in methodParamKeys:
                if type(methodParams[iKey])==list:
                    dummyDict[iKey]=None
                else:
                    dummyDict[iKey]=methodParams[iKey]

            # quickly identify which methodParamValues are lists
            listBoolVec=[type(i)==list for i in methodParamValues]
            # return these as a list of int indices
            listIndices=[i for i, x in enumerate(listBoolVec) if x]
            # if there are any elements in listIndices then there are some parameters to sweep,
            # and we create the parameter dictionaries accordingly
            if len(listIndices)>0:
                # obtain the cartesian product all list-type elements of methodParamValues
                # the sequence of resulting tuple elements for each item in the returned cartesian product
                # should correspond to the sequence of keys in methodParamKeys
                for iCombinations in itertools.product(*[methodParamValues[i] for i in listIndices]):
                    # create a copy of the dummyDict
                    workingDict=dummyDict.copy()
                    # now fill in the values from iCombinations
                    for iIndex,iKey in enumerate(listIndices):
                        workingDict[methodParamKeys[iKey]]=iCombinations[iIndex]
                    # now append the workingDict to methodParamDicts
                    methodParamDicts.append(workingDict)
            # otherwise, if there are no combinations of parameters to sweep, then just append the dummyDict
            else:
                methodParamDicts.append(dummyDict)
    # otherwise, if parameterSweep is false, then just append the methodParams dictionary to methodParamDicts
    else:
        methodParamDicts=[methodParams]

    # now we have a list of dictionaries to use for the parameter sweep
    # begin iterating over the dictionaries in methodParamDicts
    # create a list to hold the community assignments from each parameter sweep
    communityAssignmentsList=[]
    for iMethodParamDict in tqdm(methodParamDicts):
        # now iterate over the methodParamDicts
        # check if the method is louvain
        if method=='louvain':
            # now run the community detection
            communityAssignments=nx.community.louvain_communities(workingGraph,**iMethodParamDict)
        else:
            # presumably this is because we haven't yet implemented the method, so raise a not implemented error
            raise NotImplementedError('Method '+str(method)+' not yet implemented.')
        # now append the community assignments to the communityAssignmentsList
        communityAssignmentsList.append(communityAssignments)

    print('Parameter sweep complete.')

    # now we have a list of community assignments from each parameter sweep
    # we need to obtain the consensus community assignments
    # first gen an agreement matrix
    # agreementMatrix=agreementMatrixFromCommunityAssignments(communityAssignmentsList)
    return communityAssignmentsList

def agreementMatrixFromCommunityAssignments(communityAssignments):
    """
    This function takes a list of community assignments and returns the agreement matrix for those assignments.
    The agreement matrix is a square matrix with dimensions equal to the number of nodes in the graph.
    The value of each element in the matrix is the number of times the two nodes corresponding to the row and column indices were assigned to the same community.
    The diagonal elements of the matrix are the number of times the node corresponding to the row and column index were assigned to the same community, which is the same as the number of times the node was assigned to any community.
    The agreement matrix is symmetric.

    Inputs:
        communityAssignments: list
            A list of community assignments for each node in the graph.  Each element corresponds to
            an instance in which ALL nodes were assigned to communities.  Ergo, the length of communityAssignments
            corresponds to the number of times the community detection algorithm was run, while each element of communityAssignments
            should have the set of unique elements (contained within differing collections, denoting distinct communities) equal to the number of nodes in the graph.

    Outputs:
        agreementMatrix: numpy matrix
            A square matrix with dimensions equal to the number of nodes in the graph.
            The value of each element in the matrix is proportion of total runs in which the two nodes corresponding to the row and column indices were assigned to the same community.
            The diagonal elements of the matrix are the number of times the node corresponding to the row and column index were assigned to the same community.
            The agreement matrix is symmetric.

    Citation Note:  Idea originally derived from:
    bctpy.consensus_und (https://github.com/aestrivex/bctpy/blob/1b40e281eda081060707e30b68106ac1ebf54130/bct/algorithms/clustering.py#L353)
    However, the implementation here is auto-generated from GitHub Copilot.    

    Testing:
    import random
    # create some test data in which 10 nodes are assigned to 5 communities testIter Times
    testIter=10
    testCommunities=[]
    for i in range(testIter):
        # create a blank list for this iteration
        currentCommunities=[ [] for i in range(5) ]
        # fill in the currentCommunities
        for i in range(10):
            # generate the int index of the community to which this node is assigned
            currentCommunityIndex=random.randint(0,4)
            # append the node to the appropriate community
            currentCommunities[currentCommunityIndex].append(i)
        # now append the currentCommunities to the testCommunities
        testCommunities.append(currentCommunities)
    # now generate the agreement matrix
    testAgreementMatrix=agreementMatrixFromCommunityAssignments(testCommunities)
    testConsensus=consensusCommunityAssignmentFromAgreementMatrix(agreementMatrix,threshold=None,nIter=50000)
    """
    import numpy as np
    import itertools
    
    # first check that the input is a list
    if type(communityAssignments)==list:
        # raise a type error if it's not a list
        
        # now check that the elements of the list are all the same length
        # probably not a good idea, because some community detection algorithms may return different numbers of communities, this isn't k-means after all.
        # if not all([len(i)==len(communityAssignments[0]) for i in communityAssignments
        
        # get the unique elements of each element of communityAssignments
        uniqueElementsLists=[]
        for iCommunityAssignments in communityAssignments:
            # maybe it's a list of lists, maybe it's a list of tuples, maybe it's a list of sets, maybe it's a list of numpy arrays
            # we need to be robust to all of these possibilities
            quickListConvertCurrent=[list(i) for i in iCommunityAssignments]
            # dissolve the list of lists into a single list
            quickListConvertCurrent=list(itertools.chain.from_iterable(quickListConvertCurrent))
            # now get the unique elements of quickListConvertCurrent
            uniqueElementsLists.append(list(set(quickListConvertCurrent)))

        # now check that the unique elements of each element of communityAssignments are the same
        if not all([i==uniqueElementsLists[0] for i in uniqueElementsLists]):
            # raise a value error if they're not all the same
            raise ValueError('The unique elements of each element of communityAssignments are not the same.  This suggests that not all nodes were assigned to communities in each run of the community detection algorithm.')

        # now we know that all nodes were assigned to communities in each run of the community detection algorithm, and we know how many total nodes there were
        # so create a numpy array to hold the co-community assignment counts
        agreementMatrix=np.zeros((len(uniqueElementsLists[0]),len(uniqueElementsLists[0])))
        # now iterate over the community assignments
        for iCommunityAssignments in communityAssignments:
            # iterate over the elements of iCommunityAssignments
            for iElement in iCommunityAssignments:
                # iterate over the pairs of elements in iElement
                for iPair in itertools.combinations(iElement,2):
                    # increment the agreementMatrix
                    agreementMatrix[iPair[0],iPair[1]]+=1
                    agreementMatrix[iPair[1],iPair[0]]+=1
        # now divide each element of agreementMatrix by the number of runs of the community detection algorithm, which is the length of communityAssignments
        agreementMatrixNorm=agreementMatrix/len(communityAssignments)
        # now return the agreementMatrix
    elif isinstance(communityAssignments,np.ndarray):
        # if the input is a numpy array, lets assume that each row is a complete assignment of all the nodes
        # and that the columns are the nodes.  The integer values in the array are the community assignments

        # sp first create an array to store the results in, it should have the same size as the number of columns in the communityAssignments
        agreementMatrix=np.zeros((communityAssignments.shape[1],communityAssignments.shape[1]))
        # now iterate over the rows of communityAssignments
        for iRow in communityAssignments:
            # get the unique elements of iRow, which are the communities
            uniqueElements=np.unique(iRow)
            # now iterate over the unique elements
            for iElement in uniqueElements:
                # idetify the indices of iRow that are equal to iElement
                iElementIndices=np.where(iRow==iElement)[0]
                # now iterate over the pairs of elements in iElementIndices
                for iPair in itertools.combinations(iElementIndices,2):
                    # increment the agreementMatrix
                    agreementMatrix[iPair[0],iPair[1]]+=1
                    agreementMatrix[iPair[1],iPair[0]]+=1
        # now divide each element of agreementMatrix by the number of runs of the community detection algorithm, which is the length of communityAssignments
        agreementMatrixNorm=agreementMatrix/len(communityAssignments)
    return agreementMatrixNorm

def hierarchicalconsensusCommunityAssignmentFromAgreementMatrix(agreementMatrix,threshold=None,nIter=5000):
    """
    This function iterates upon consensusCommunityAssignmentFromAgreementMatrix to begin 
    forming hierarchical community assignments--that is community assignments of community assignments.

    Thus, within how this algorithm is implented, the nodes are reprsented by integers, with a list of
    these corresponding to the community assignments of the nodes.  In turn, these lists can also be 
    clustered, and the clusters of these lists can be clustered, and so on.  This algorithm will do so
    in a fashion that maximizes the relationship between nodes and communities of nodes.

    Parameters
    ----------
    agreementMatrix : numpy matrix
        A square matrix with dimensions equal to the number of nodes in the graph.
        The value of each element in the matrix is proportion of total runs in which the two nodes corresponding to the row and column indices were assigned to the same community.
        The diagonal elements of the matrix are the number of times the node corresponding to the row and column index were assigned to the same community.  Should be none, as nodes aren't duplicated in the same community.
        The agreement matrix is symmetric.
    threshold : float, optional

    
    
    
    """

    # begin by randomly combining t


    # we begin by running consensusCommunityAssignmentFromAgreementMatrix to get the initial clusters
    initialCommunities=consensusCommunityAssignmentFromAgreementMatrix

    # now that we have these we need to determine which communities (as reprsented by lists of nodes)
    # most sensibly are related

def computeCommunityLiklehoods(communityAssignments,agreementMatrix,weighted=True,bias=False):
    """
    This function computes the likelihood of each community assignment in communityAssignments
    given the agreementMatrix.  The likelihood is computed as the product of the probabilities
    of the nodes in each community being assigned to the same community.

    Parameters
    ----------
    
    """

    import itertools
    import numpy as np
    communityLikelihoods=[]
    for iCommunityAssignment in communityAssignments:
        # iterate over the pairs of nodes in iCommunityAssignment
        iCommunityLikelihood=1
        # assuming that there are more than two nodes in the community
        if len(iCommunityAssignment)>=2:
            for iPair in itertools.combinations(iCommunityAssignment,2):
                # multiply the likelihood by the probability of the nodes being assigned to the same community
                iCommunityLikelihood*=agreementMatrix[iPair[0],iPair[1]]
            # append the community likelihood to communityLikelihoods
            communityLikelihoods.append(iCommunityLikelihood)
        # otherwise append the minimum non-zero value in agreementMatrix
        else:
            communityLikelihoods.append(np.min(agreementMatrix[agreementMatrix!=0]))
        # if weighted==True
    if weighted:
            weightVector=[len(list(itertools.combinations(x,2))) for x in communityAssignments]
            # now add in a bias that multiplies the likelihood by
            if bias:
                biasVal=1.2
                weightVector=[(x*((biasVal**x))+(1-biasVal)) for x in weightVector]
            communityLikelihoodsWeighted=np.array(communityLikelihoods)*np.array(weightVector)
            communityLikelihoods=communityLikelihoodsWeighted
        
    return communityLikelihoods


def consensusCommunityAssignmentFromAgreementMatrix(agreementMatrix,threshold=.05,nIter=5000):
    """
    This function takes an agreement matrix and returns a consensus community assignment.
    It permutes possible community assignments and returns the one that maximizes the agreement matrix.
    
    Parameters
    ----------
    agreementMatrix : numpy matrix
        A square matrix with dimensions equal to the number of nodes in the graph.
        The value of each element in the matrix is proportion of total runs in which the two nodes corresponding to the row and column indices were assigned to the same community.
        The diagonal elements of the matrix are the number of times the node corresponding to the row and column index were assigned to the same community.  Should be none, as nodes aren't duplicated in the same community.
        The agreement matrix is symmetric.
    threshold : float, optional
        The threshold above which to consider two nodes as belonging to the same community.  The default is None.
    nIter : int, optional
        The number of iterations to run.  The default is 1000.

    Returns
    -------
    consensusCommunityAssignment : list
        A list of community assignments for each node in the graph.  Each element corresponds to
        an instance in which ALL nodes were assigned to communities.  Ergo, the length of communityAssignments
        corresponds to the number of times the community detection algorithm was run, while each element of communityAssignments
        should have the set of unique elements (contained within differing collections, denoting distinct communities) equal to the number of nodes in the graph.
    
    """
    # how many nodes to remove from communities during the erosion step
    erosionFactor=2

    import numpy as np
    import random
    import itertools
    # also import for loop reporting
    from tqdm import tqdm
    # start by creating a list of community assignments with two (or three, if rounding necessitates) members each
    # each member of the list is a list of the nodes assigned to that community
    # compte if the number of nodes is odd
    if agreementMatrix.shape[0]%2==1:
        # if the number of nodes is odd, then we need to a community with three members
        # create a holder list of lists, wherein each list two placeholder items (None) long, except for the last list, which is three placeholder items long
        communityAssignments=[ [None,None] for i in range(int(agreementMatrix.shape[0]/2)-1) ]+[[None,None,None]]
        # otherwise, if the number of nodes is even
    else:
        # create a holder list of lists, wherein each list two placeholder items (None) long
        communityAssignments=[ [None,None] for i in range(int(agreementMatrix.shape[0]/2)) ]
    # now iterate over these community pairings and assign unassigned nodes to them.
    # first identify the unassigned nodes, which are all of them to start
    unassignedNodes=list(range(agreementMatrix.shape[0]))
    assignedNodes=[]
    # now iterate over the community assignments
    for iCommunityAssignment in communityAssignments:
        # for each element of iCommunityAssignment, assign a random unassigned node to it
        for i in range(len(iCommunityAssignment)):
            # randomly select an unassigned node
            randomNode=random.choice(unassignedNodes)
            # assign the node to the current community assignment
            iCommunityAssignment[i]=randomNode
            # remove the node from the unassigned nodes
            unassignedNodes.remove(randomNode)
            # add the node to the assigned nodes
            assignedNodes.append(randomNode)

    # for each community, compute the combinatorial probability of that particular community assignment
    # this is the product of the probabilities of each pair of nodes being assigned to the same community


    # find the lowest non zero value in the agreement matrix
    minAgreement=np.min(agreementMatrix[agreementMatrix!=0])
    # if threshold is None, then set it to the minimum agreement
    if threshold is None:
        # actually use the average agreement from the agreement matrix
        threshold=np.mean(agreementMatrix)
        # threshold=minAgreement

    # now iterate over the community assignments and compute the likelihood of each community assignment with tqdm
    for iIters in range(nIter):
        # print('Iteration '+str(iIters)+' of '+str(nIter),end='\r')
        # compute the likelihood of each community assignment
        communityLikelihoods=computeCommunityLiklehoods(communityAssignments,agreementMatrix ,weighted=True)
        # weight this by the number of pairwise combinations of nodes in each community
        # print the sum of the community likelihoods, in place
        print('Sum of community likelihoods: '+str(np.sum(communityLikelihoods)),end='\r')

        # identify the lowest 1/10 (or closest integer thereof) of community assignments, as defined by the 1/10 of the nodes being in the lowest likelyhood communities
        # this 1/10 th heuristic is what we'll use for now, we'll come back with a more principled approach later
        # these are the communities that we will dissolve, and reassign to the nodes of other communities
        # HOWEVER, half of these dissolved communties will be reinitialized as new community pairs, and half will be added to existing community pairs
        # start by arranging the community assignments in order of likelihood, from lowest to highest
        communityAssignmentsOrdered=[x for _,x in sorted(zip(communityLikelihoods,communityAssignments))]
        # if it's the last run, then we want to return the community assignments
        nodesToReassign=[0]
        if iIters==nIter-1 or (len(nodesToReassign)==0 and all(communityLikelihoods>threshold)) :
            print('Returning community assignments')
            #return communityAssignmentsOrdered
        # identify how many nodes need to be reassigned
        # nNodesToReassign=int(np.floor(len(communityAssignmentsOrdered)/6))

        # find out how many nodes to reassign based on iterThresholds and propThresholds
        # use iterThresholds to find out which iter threshold is the most recently passed

        # identify the groups in communityLikelihoods that have less than the threshold likelihood
        # these are the groups that we will dissolve
        groupsToDissolve=np.where(communityLikelihoods<threshold)[0]
        nodesToReassign=[]
        for iGroups in groupsToDissolve:
            # add the nodes in this group to the list of nodes reassign
            nodesToReassign.extend(communityAssignmentsOrdered[iGroups])
            # now remove these nodes from the community assignments
        # reform the community assignments by removing the groups to dissolve
        communityAssignmentsOrdered=[x for i,x in enumerate(communityAssignmentsOrdered) if i not in groupsToDissolve]
        # assuming there is at least 2 community assignment available
        if len(communityAssignmentsOrdered)>2:
            
            for iNode in nodesToReassign:           
               # get the liklehood of the current community assignments
                currentAssignmentLikelihoods=computeCommunityLiklehoods(communityAssignmentsOrdered,agreementMatrix,weighted=True)
                # copy these community lists to a new list
                communityAssignmentsCopy=[]
                # add the node to each of them
                for i in range(len(communityAssignmentsOrdered)):
                    tempGroupAddition=communityAssignmentsOrdered[i]+[iNode]
                    communityAssignmentsCopy.append(tempGroupAddition)
                # compute the likelihood of each of these community assignments
                possibleCommunityAssignmentsLikelihoods=computeCommunityLiklehoods(communityAssignmentsCopy,agreementMatrix,weighted=True)
                # get the difference between the current assignment likelihoods and the new assignment likelihoods
                incrementDifference=np.array(possibleCommunityAssignmentsLikelihoods)-np.array(currentAssignmentLikelihoods)
                # find the "no chance" locations, where both the pre (currentAssignmentLikelihoods) and post (iRandomCommunityAssignmentsLikelihoods) likelihoods are equal to zero
                noChanceLocations=np.where(np.logical_and(np.array(currentAssignmentLikelihoods)==0,np.array(possibleCommunityAssignmentsLikelihoods)==0))[0]
                
                
                # find the index of the difference corresponding to the largest 
                iHighestLikelihoodCommunityAssignment=np.argmax(incrementDifference)
                # find the index of the community assignment with the highest likelihood
                # iHighestLikelihoodCommunityAssignment=np.argmax(iRandomCommunityAssignmentsLikelihoods)
                # add the node to this community assignment
                # if the hit to the likelihood is greater than the negative of the lowest nonzero likelihood in the agreementMatrix, then just create a new singleton community with it
                if possibleCommunityAssignmentsLikelihoods[iHighestLikelihoodCommunityAssignment]>=-threshold and iHighestLikelihoodCommunityAssignment not in noChanceLocations:
                    
                    communityAssignmentsOrdered[iHighestLikelihoodCommunityAssignment].append(iNode)
                else:
                    communityAssignmentsOrdered.append([iNode])
        # otherwise, just randomly create groups of between 1 and 3 nodes until all of the nodesToReassign are reassigned
        else:
            """
            # while there are still nodes to reassign
            while len(nodesToReassign)>3:
                # randomly select a number of nodes to reassign, between 1 and 3
                iNodesToReassign=random.sample(nodesToReassign,random.choice([1,2,3]))
                # remove these nodes from the nodesToReassign
                for iNode in iNodesToReassign:
                    nodesToReassign.remove(iNode)
                # add these nodes to a new community assignment
                communityAssignmentsOrdered.append(iNodesToReassign)
                # if there are still nodes to reassign, create a new community with them
            if len(nodesToReassign)>0:
                communityAssignmentsOrdered.append(nodesToReassign)
            """
            pass

        # if the current iteration is a multiple of 100 then we'll do a bit or erosion / shuffling
        if iIters%100==0:
            # iterate across the communityAssignmentsOrdered elements, and if there are more than erosionFactor * 2 elements in it, remove the 
            # lowest performing erosionFactor elements 
            groupsToAdd=[]
            for i in range(len(communityAssignmentsOrdered)):
                # if there are more than erosionFactor * 2 elements in it, remove the lowest performing erosionFactor elements
                if len(communityAssignmentsOrdered[i])>=erosionFactor*2:
                    # find which are the erosionFactor lowest performing elements
                    # compute the likelihood of the current community assignments after removing each individual node
                    # create holder for the likelihoods
                    tempLikelihoods=np.zeros(len(communityAssignmentsOrdered[i]))
                    for iSimulations in range(len(communityAssignmentsOrdered[i])):
                        # create a mask of communityAssignmentsOrdered[i] with the iSimulations element removed and compute the likelihood of this
                        tempMask=np.logical_not(np.array(communityAssignmentsOrdered[i])==communityAssignmentsOrdered[i][iSimulations])
                        # compute the likelihood of this mask
                        # apply the mask
                        tempNodes=[x for i,x in enumerate(communityAssignmentsOrdered[i]) if tempMask[i]]
                        tempLikelihoods[iSimulations]=computeCommunityLiklehoods([tempNodes],agreementMatrix,weighted=True)
                    # find the erosionFactor lowest performing elements
                    iLowestPerformingIndexes=np.argsort(tempLikelihoods)[0:erosionFactor]
                    # index back into communityAssignmentsOrdered[i] to find the nodes to remove
                    iLowestPerforming=[communityAssignmentsOrdered[i][x] for x in iLowestPerformingIndexes]
                    # remove these elements from communityAssignmentsOrdered[i]
                    [communityAssignmentsOrdered[i].remove(x) for x in iLowestPerforming]
                    # create a new community with these elements and add it to groupsToAdd
                    groupsToAdd.append(list(iLowestPerforming))
                    
            # add the groupsToAdd to communityAssignmentsOrdered
            communityAssignmentsOrdered.extend(groupsToAdd)

        # now reassign communityAssignmentsOrdered to communityAssignments
        communityAssignments=communityAssignmentsOrdered

def reorderPandasDFAxesElements(pandasDF,indexesOrder=None,columnsOrder=None):
    """
    Reorder the indexes and columns of a pandas dataframe according to the indexesOrder and columnsOrder
    
    Parameters:
        pandasDF (pandas.DataFrame): Pandas dataframe to reorder
        indexesOrder (list): List of int, indicating desired sequence of current indexes
        columnsOrder (list): List of int, indicating desired sequence of current columns
        
    Returns:
        pandasDF (pandas.DataFrame): Pandas dataframe with reordered indexes and columns
    """
    import numpy as np
    import pandas as pd
    # check and make sure that indexesOrder and columnsOrder are unique
    if len(indexesOrder)!=len(set(indexesOrder)):
        raise ValueError('indexesOrder contains duplicate elements')
    if len(columnsOrder)!=len(set(columnsOrder)):
        raise ValueError('columnsOrder contains duplicate elements')


    # copy the pandasDF
    pandasDF=pandasDF.copy()
    # get the indexes and columns
    indexes=list(pandasDF.index)
    columns=list(pandasDF.columns)
    # also get the data
    data=pandasDF.values

    # create a new ouput array that is blank
    firstShift=np.zeros(data.shape)
    if not type(indexesOrder)==type(None):
        # Take the elements of data and put them in the correct order indicated by indexesOrder
        firstShift=data[indexesOrder,:]
    # otherwise just take the data as is
    else:
        firstShift=data
    # create a new ouput array that is blank
    secondShift=np.zeros(data.shape)
    if not type(columnsOrder)==type(None):
        # Take the elements of data and put them in the correct order indicated by columnsOrder
        secondShift=firstShift[:,columnsOrder]
    # otherwise just take the data as is
    else:
        secondShift=firstShift
    # create a new pandas dataframe with the new indexes and columns
    # but first resourt the indexes and columns
    if not type(indexesOrder)==type(None):
        resortedIndexes=[indexes[x] for x in indexesOrder]
    else:
        resortedIndexes=indexes
    if type(columnsOrder)==type(None):
        resortedColumns=[columns[x] for x in columnsOrder]
    else:
        resortedColumns=columns
    dfOut=pd.DataFrame(secondShift,index=indexes,columns=columns)

    return dfOut

def consensus_partition(agreement_matrix, threshold, num_reps=1000, random_seed=None):
    '''
    Seek a consensus partition of an agreement matrix.
    
    Parameters:
        agreement_matrix (np.ndarray): NxN agreement matrix with probabilities of nodes being in the same cluster.
        threshold (float): Threshold for agreement matrix to control the resolution of reclustering.
        num_reps (int): Number of times the clustering algorithm is reapplied. Default is 1000.
        random_seed (hashable, optional): Seed for random number generation. If None, use the global random state.

    Returns:
        consensus_partition (np.ndarray): Consensus partition as a 1D array.

    Note this is a reimplementation of bctpy's
    https://github.com/aestrivex/bctpy/blob/1b40e281eda081060707e30b68106ac1ebf54130/bct/algorithms/clustering.py#L353

    Testing
    -------
    # assuming you have an agreement matrix called agreementMatrix
    threshold=.05
    num_reps=1000
    random_seed=None
    agreement_matrix=agreementMatrix
    consensusPartitionOut=consensus_partition(agreement_matrix,threshold,num_reps,random_seed)


    '''
    import numpy as np
    import networkx as nx

    # Initialize random number generator
    rng = np.random.default_rng(seed=random_seed)
    
    def unique_partitions(partitions):
        # Relabel partitions to recognize different numbers on the same topology
        # maybe this can be implemented by applying a rule:
        # partition elements should be numbered in sequence of their earliest node appearance
        # lets implement this rule
        # create a copy that will be the output
        partitionsOut=partitions.copy()


        for i in range(len(partitionsOut)):
            # take the ith row
            ithRow=partitionsOut[i,:].copy()
            # get the unique elements
            uniqueElements=np.unique(ithRow)
            # return the first instance of each unique element using list comprehension
            firstInstances=[np.where(ithRow==x)[0][0] for x in uniqueElements]
            # find the indexes assoiated with each unique element (e.g. group)
            indexes=[np.where(ithRow==x)[0] for x in uniqueElements]
            # iterate across the unique elements and for each one change the record
            # in partitionsOut corresponding to the current row of indexes to be the
            # number firstInstance values that are less than the current element's firstInstance
            for iUniqueElement in range(len(uniqueElements)):
                # get the current unique element
                currentUniqueElement=uniqueElements[iUniqueElement]
                # get the current first instance
                currentFirstInstance=firstInstances[iUniqueElement]
                # get the current indexes
                currentIndexes=indexes[iUniqueElement]
                # get the number of firstInstance values that are less than the current element's firstInstance
                numLessThanCurrent=np.sum(np.array(firstInstances)<currentFirstInstance)
                # change the record in partitionsOut corresponding to the current row of indexes to be the
                # number firstInstance values that are less than the current element's firstInstance
                ithRow[currentIndexes]=numLessThanCurrent
                # print the current row contents
                #print(str(ithRow))
            # replace the current row of partitionsOut with the new ithRow
            partitionsOut[i,:]=ithRow

        # find which of these rows are unique
        uniqueRows=np.unique(partitionsOut,axis=0)
        # return the unique rows
        return uniqueRows


    num_nodes = len(agreement_matrix)
    flag = True

    # Iteratively build consensus partition
    while flag:
        flag = False
        thresholded_matrix = agreement_matrix * (agreement_matrix >= threshold)
        np.fill_diagonal(thresholded_matrix, 0)

        if np.size(np.where(thresholded_matrix == 0)) == 0:
            # All nodes are singleton communities
            consensus_partition = np.arange(1, num_nodes + 1)
        else:
            outGroupingsArray = np.zeros((num_nodes, num_reps))
            
            # test to get parameter space
            #resolutionBounds=quickTestLouvainResolutionParamRange(agreement_matrix,minDesiredGroupings=4,maxDesiredGroupings=None,verbose=False)


            #methodParams={'resolution': list(np.linspace(resolutionBounds[0],.1,sampleSpace)),'seed':[None for x in range(int(np.ceil(num_reps/sampleSpace)))]}
            methodParams={'resolution': 1 ,'seed':[None for x in range(int(np.ceil(num_reps)))]}
                # go ahead and use networkx to get the graph of the input agreement matrix
            if   isinstance(agreement_matrix, np.ndarray):
                networkxGraph=nx.from_numpy_array(agreement_matrix)
            elif isinstance(agreement_matrix, np.matrix):
                networkxGraph=nx.from_numpy_matrix(agreement_matrix)
            elif isinstance(agreement_matrix, nx.Graph):
                networkxGraph=agreement_matrix
            testCommunities=detectCommunitiesFromMatrix(networkxGraph,method='louvain',parameterSweep=True,methodParams=methodParams)
            # convert the test community outputs to the expected format
            outGroupings=[convertListsOfNodeGroupings_to_identityVector(x) for x in testCommunities]
            # convert to a numpy array
            outGroupingsArray=np.array(outGroupings)
            
            # Obtain unique partitions
            consensus_partition = unique_partitions(outGroupingsArray)
            num_unique_partitions = np.size(consensus_partition, axis=0)
            
            if num_unique_partitions > 1:
                # print('Number of unique partitions: ' + str(num_unique_partitions))
                print('Number of unique partitions: ' + str(num_unique_partitions) + ' out of ' + str(num_reps))
                flag = True
                # Update agreement matrix for next iteration
                agreement_matrix = agreementMatrixFromCommunityAssignments(outGroupingsArray)

    # Return consensus partition
    squoze_partition = np.squeeze(consensus_partition )

    return squoze_partition



def convertListsOfNodeGroupings_to_identityVector(listOfNodeGroupings):
    """
    This function converts a list of node groupings, as is the standard output of the 
    networkx community detection algorithms, into a vector of community assignments,
    with integers indicating the community group assignment of each node.
    
    Parameters
    ----------
    listOfNodeGroupings : list of lists of integers
        A list of lists of integers, where each sublist contains the nodes in a community.

    Returns
    -------
    identityVector : numpy array of integers
        A vector of integers indicating the community group assignment of each node.  The sequence position
        of the integer indicates the node number.
    
    """
    import collections
    import numpy as np
    # first dissolve the list of lists into a single list in order to get a unique list of nodes
    completeListOfNodes = []
    for nodeGrouping in listOfNodeGroupings:
        completeListOfNodes.extend(nodeGrouping)

    # check if any nodes are repeated and throw an error if so
    if len(completeListOfNodes) != len(set(completeListOfNodes)):
        # find the repeated nodes
        repeatedNodes = [item for item, count in collections.Counter(completeListOfNodes).items() if count > 1]
        raise ValueError('The following nodes are repeated in the list of node groupings: ' + str(repeatedNodes))
    
    # if not, find the total number of nodes
    numNodes = len(completeListOfNodes)
    # create an output vector of zeros to be filled in
    identityVector = np.zeros((numNodes,), dtype=int)

    # iterate through the list of node groupings and fill in the identity vector
    for communityIndex, nodeGrouping in enumerate(listOfNodeGroupings):
        for node in nodeGrouping:
            identityVector[node] = communityIndex

    return identityVector

def quickTestLouvainResolutionParamRange(inputMatrix,minDesiredGroupings=4,maxDesiredGroupings=None,verbose=False):
    """
    This function performs a quick test of the Louvain algorithm over a range of resolution parameters in order
    to determine the parameter range which yeilds results within the desired range of groupings.  This is useful
    for determining the range of resolution parameters to use for a more thorough search.

    Parameters
    ----------
    inputMatrix : numpy array
        An NxN numpy array representing the input matrix to be clustered.
    minDesiredGroupings : int
        The minimum number of desired groupings to be found by the Louvain algorithm.  The default is 4.
    maxDesiredGroupings : int
        The maximum number of desired groupings to be found by the Louvain algorithm.  The default is None which will 
        compute a maxDesiredGroupings parameter based upon a heuristic of allowing for ~ 4 nodes per group.
    verbose : bool
        A boolean value indicating whether or not to print the results of the quick test.  The default is False.

    Returns
    -------
    resolutionParameterRange : tuple of floats
        A tuple containing the minimum and maximum resolution parameters to use for a more thorough search.
        Within this range, Louvain clusterings can be expected to return the desired number of groupings.
    """
    import networkx as nx
    import numpy as np

    # set some internal parameters
    initialMaxResolutionParameter=2
    initialMinResolutionParameter=.5
    repeatIterations=5
    samples=10
    startPoint=1
    stepChange=.05
    
    # maybe you need to set the diagonal to true?
    # np.fill_diagonal(inputMatrix,1)

    # parse the inputMatrix into a networkx graph
    if   isinstance(inputMatrix, np.ndarray):
       
        networkxGraph=nx.from_numpy_array(inputMatrix)
    elif isinstance(inputMatrix, np.matrix):
        networkxGraph=nx.from_numpy_matrix(inputMatrix)
    elif isinstance(inputMatrix, nx.Graph):
        networkxGraph=inputMatrix

    # determine the number of nodes in the graph
    numNodes=networkxGraph.number_of_nodes()

    # determine the maximum number of desired groupings if not specified
    if maxDesiredGroupings is None:
        maxDesiredGroupings=int(np.ceil(numNodes/4))
        # also set the error margin to be 1/10th of the maxDesiredGroupings
        errorMargin=int(np.ceil(maxDesiredGroupings/10))

    desiredRangeFound=False
    # set current maxResolutionParameter and minResolutionParameter
    currentMaxResolutionParameter=initialMaxResolutionParameter
    currentMinResolutionParameter=initialMinResolutionParameter
    # initalize vectors for both the current and previous grouping results
    currentGroupingResults=np.zeros((samples))
    previousGroupingResults=np.zeros((samples))
    unchangedCounter=0

    while not desiredRangeFound:
        # print the current resolution parameter range
        if verbose:
            print('Current resolution parameter range: ' + str(currentMinResolutionParameter) + ' to ' + str(currentMaxResolutionParameter))

        # initialize the resolution parameter range as a linear range with 100 samples
        resolutionParameterRange_aboveOne=np.logspace(np.log10(startPoint),np.log10(currentMaxResolutionParameter),5)
        resolutionParameterRange_belowOne=np.logspace(np.log10(startPoint),np.log10(currentMinResolutionParameter),5)
        # merge and sort the two ranges
        resolutionParameterRange=np.sort(np.concatenate((resolutionParameterRange_aboveOne,resolutionParameterRange_belowOne)))
        # run the Louvain algorithm over the resolution parameter range, with repeatIterations repeats per resolution parameter and compute the number of groupings obtained from each run

        numGroupings=np.zeros((len(resolutionParameterRange),repeatIterations))
        for resolutionParameterIndex,resolutionParameter in enumerate(resolutionParameterRange):
            for repeatIndex in range(repeatIterations):
                communityAffiliation=list(nx.community.louvain_communities(networkxGraph,weight='weight',resolution=resolutionParameter))
                numGroupings[resolutionParameterIndex,repeatIndex]=len(communityAffiliation)
            
        # compute the mean number of groupings obtained for the resolution parameters
        meanNumGroupings=np.mean(numGroupings,axis=1)
        # set the currentGroupingResults to be the meanNumGroupings
        currentGroupingResults=meanNumGroupings
        # check if the current and previous grouping results are the same
        if np.array_equal(currentGroupingResults,previousGroupingResults):
            # increment the unchanged counter
            unchangedCounter=unchangedCounter+1
        # check if the unchanged counter is greater than 5
        if unchangedCounter > 5:
            # throw an error, because we are stuck in a loop
            raise ValueError('The quick test of the Louvain algorithm is stuck in a loop.  There may be a problem with the input matrix.')
        # print the mean number of groupings obtained for the resolution parameters
        if verbose:
            print('Mean number of groupings obtained for the resolution parameters: ' + str(meanNumGroupings))
        currentMaxGroupings=np.max(meanNumGroupings)
        currentMinGroupings=np.min(meanNumGroupings)
        
        # check if proximity of the max and min resolution parameters to the maximum desired number of groupings
        if currentMaxGroupings < maxDesiredGroupings and abs(currentMaxGroupings-maxDesiredGroupings) > errorMargin:
            # then we need to increase the max resolution parameter, because:
            # "If resolution is less than 1, the algorithm favors larger communities. Greater than 1 favors smaller communities"
            currentMaxResolutionParameter=currentMaxResolutionParameter*(1+stepChange)
        elif currentMaxGroupings > maxDesiredGroupings and abs(currentMaxGroupings-maxDesiredGroupings) > errorMargin:
            # then we need to decrease the max resolution parameter, because:
            # "If resolution is less than 1, the algorithm favors larger communities. Greater than 1 favors smaller communities"
            currentMaxResolutionParameter=currentMaxResolutionParameter/(1+stepChange)
        # also test the min resolution parameter
        if currentMinGroupings > minDesiredGroupings and np.abs(currentMinGroupings-minDesiredGroupings) > 1:
            # then we need to decrease the min resolution parameter, because:
            # "If resolution is less than 1, the algorithm favors larger communities. Greater than 1 favors smaller communities"
            currentMinResolutionParameter=currentMinResolutionParameter/(1+stepChange)
        elif currentMinGroupings < minDesiredGroupings and np.abs(currentMinGroupings-minDesiredGroupings) > 1:
            # then we need to increase the min resolution parameter, because:
            # "If resolution is less than 1, the algorithm favors larger communities. Greater than 1 favors smaller communities"
            currentMinResolutionParameter=currentMinResolutionParameter*(1+stepChange)

        # do a test to see if all conditions are met
        if abs(currentMaxGroupings-maxDesiredGroupings) <= errorMargin and np.abs(currentMinGroupings-minDesiredGroupings) <= 1:
            # then we have found the desired range
            desiredRangeFound=True
        # find the log_10 based midpoint between the current max and min resolution parameters
        log10Midpoint=np.log10(currentMaxResolutionParameter)-np.log10(currentMinResolutionParameter)
        # compute the value this represents in the linear space
        startPoint=10**log10Midpoint
        #set the current currentGroupingResults to be the previousGroupingResults
        previousGroupingResults=currentGroupingResults
    print('Desired range found: ' + str(currentMinResolutionParameter) + ' to ' + str(currentMaxResolutionParameter))
    return (currentMinResolutionParameter,currentMaxResolutionParameter)



    