# -*- coding: utf-8 -*-
# @Author: GigaFlower
# @Date:   2016-12-27 21:45:08
# @Last Modified by:   GigaFlower
# @Last Modified time: 2017-01-01 22:00:05

from __future__ import with_statement, print_function

import os
from time import time
import lucene

from website.core.index.utility import theme_colors_for_web

# nasty Lucene imports
from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
# end

BASE_DIR = os.path.dirname(__file__)
LUCENE_INDEX_DIR = os.path.join(BASE_DIR, 'web.index')
LUCENE_CATELOG_FILE = os.path.join(BASE_DIR, 'web.index', 'PICTURES.txt')

FILE_FIELD_FORMAT = ["ind", "ent_name", "info", "keywords", "imgurl"]
STORE_FIELDS = ["filename", "ent_name", "info", "theme_colors"]
INDEX_FIELDS = ["ent_name", "keywords", "n_colors"]
ADD_FIELDS = STORE_FIELDS + INDEX_FIELDS

FIELD_FUNCS = {
    "filename" : lambda f:"{:05d}".format(int(f['ind'])) + '.jpg',
    "keywords" : lambda f:f['keywords'].replace('%', ' '),
    "theme_colors" : lambda f:" ".join(theme_colors_for_web(f['filename'])),
    "n_colors" : lambda f:str(f['theme_colors'].count(' '))
}


def create_index():
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print('lucene %s is working ...' % lucene.VERSION)

    start = time()
    with open(LUCENE_CATELOG_FILE, 'r') as index_f:
        index_files(storeDir=LUCENE_INDEX_DIR, indexFile=index_f)
    end = time()

    print("time consumed: %.5f" % (end - start))


def index_files(storeDir, indexFile):
    store = SimpleFSDirectory(File(storeDir))
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)

    config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)

    writer = IndexWriter(store, config)

    index_docs(indexFile, writer)

    print('commit index')
    writer.commit()
    writer.close()
    print('done')


def index_docs(indexFile, writer):
    FIELD_PARA = {f: (
        Field.Store.YES if f in STORE_FIELDS else Field.Store.NO,
        Field.Index.ANALYZED if f in INDEX_FIELDS else Field.Index.NO,
    ) for f in ADD_FIELDS}

    for line in indexFile:

        fields = dict(zip(FILE_FIELD_FORMAT, line.split('\t')))

        # fields['filename'] = "{:05d}".format(int(fields['ind'])) + '.jpg'
        # fields['keywords'] = fields['keywords'].replace('%', ' ')
        for f in ADD_FIELDS:
            if f in FIELD_FUNCS:
                fields[f] = FIELD_FUNCS[f](fields)

        print("adding %s" % fields['ind'])

        try:
            doc = Document()

            for f in ADD_FIELDS:
                doc.add(Field(f, fields[f], *FIELD_PARA[f]))

            writer.addDocument(doc)

        except Exception, e:
            print("Failed in indexDocs: %r" % e)
