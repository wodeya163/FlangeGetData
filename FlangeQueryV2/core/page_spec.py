# -*- coding: utf-8 -*-
"""页面声明模型：前 4 个字段保持既有 4 元组协议，扩展字段为可选元数据。"""

FIELDS = ('name', 'csvf', 'template', 'labels', 'code', 'group', 'tab',
          'kind', 'subtype', 'drawing', 'filters', 'columns', 'dimensions',
          'controls', 'provenance')


class PageSpec:
    """页面规格。

    ``len(page)`` / 迭代 / 切片只暴露前 4 个字段，兼容既有
    ``name, csvf, tpl, labels = page`` 解包；扩展字段通过属性访问。
    """

    __slots__ = FIELDS

    def __init__(self, name, csvf, template, labels, code='', group='', tab='',
                 kind='', subtype='', drawing='', filters=(), columns=(),
                 dimensions=(), controls=(), provenance=''):
        self.name = name
        self.csvf = csvf
        self.template = template
        self.labels = labels
        self.code = code
        self.group = group
        self.tab = tab
        self.kind = kind
        self.subtype = subtype
        self.drawing = drawing
        self.filters = filters
        self.columns = columns
        self.dimensions = dimensions
        self.controls = controls
        self.provenance = provenance

    @property
    def stem(self):
        return self.csvf[:-4] if self.csvf.lower().endswith('.csv') else self.csvf

    def _asdict(self):
        return {name: getattr(self, name) for name in FIELDS}

    def __iter__(self):
        yield self.name
        yield self.csvf
        yield self.template
        yield self.labels

    def __len__(self):
        return 4

    def __getitem__(self, index):
        values = (self.name, self.csvf, self.template, self.labels)
        return values[index]

    def __repr__(self):
        return 'PageSpec(%r, %r, %r, ...)' % (self.name, self.csvf,
                                               self.template)

    def with_meta(self, **kwargs):
        data = self._asdict()
        data.update(kwargs)
        return PageSpec(**data)
