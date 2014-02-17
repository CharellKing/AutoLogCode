#coding=utf-8

def camel_to_underline(camel_format):  
    ''''' 
        驼峰命名格式转下划线命名格式 
    '''  
    underline_format=''  
    if isinstance(camel_format, str):  
        for _s_ in camel_format:  
            underline_format += _s_ if _s_.islower() else '_'+_s_.lower()  
    return underline_format  
      
def underline_to_camel(underline_format):  
    ''''' 
        下划线命名格式驼峰命名格式 
    '''  
    camel_format = ''  
    if isinstance(underline_format, str):  
        for _s_ in underline_format.split('_'):  
            camel_format += _s_.capitalize()  
    return camel_format

class FieldFmt (object):
    def __init__(self, name, fmt):
        self.name = name
        self.fmt = fmt
    
    def GetName(self):
        return self.name
    
    def GetFmt(self):
        return self.fmt
    

class FieldType (object):
    def __init__(self, name, ty, comment):
        self.name = name
        self.type = ty
        self.comment = comment
    
    def GetName(self):
        return self.name
    
    def GetType(self):
        return self.type
    
    def GetComment(self):
        return self.comment
    
class Field (object):
    def __init__(self, attr):
        self.name = attr[0]
        self.type = attr[1]
        self.len = attr[2]
        self.comment = attr[3]
    
    def GetFormat(self):
        fmt = ""
        if "bigint" == self.type:
            fmt = "%lld"
        elif "int" == self.type:
            fmt = "%d"
        elif "varchar" == self.type:
            fmt = "'%s'"
        elif "timestamp" == self.type:
            fmt = "FROM_UNIXTIME(%lld)"
        else:
            print "unknown type"
        return FieldFmt(self.name, fmt)
    
    def GetType(self):
        field_type = ""
        if "bigint" == self.type:
            field_type = "LLong"
        elif "int" == self.type:
            field_type = "int"
        elif "varchar" == self.type:
            field_type = "string"
        elif "timestamp" == self.type:
            field_type = "LLong"
        else:
            print "unkonw type"
        return field_type
    
    def GetParam(self):
        if "varchar" == self.type:
            return self.name + ".c_str()"
        return self.name
    
    def GetCreateType(self):
        if "varchar" == self.type:
            return "varchar(" + self.len + ")"
        if ("timestamp" == self.type):
            return "timestamp ON UPDATE CURRENT_TIMESTAMP"
        return self.type
    
    def GetComment(self):
        return self.comment
    
    def GetName(self):
        return self.name
    
    def __repr__(self):
        return "%s\t%s\t%d\n" %(self.name, self.type, int(self.len))
    
    __str__ = __repr__
    
class Table (list):
    def __init__(self, tablename, comment):
        self.tablename = tablename
        self.comment = comment
        
    def AddField(self, field):
        self.append(field);
    
    def GetTableName(self):
        return self.tablename
    
    def GetTableComment(self):
        return self.comment
    
    def ShowCallInit(self):
        return self.GetStructName() + "::" + "Init(this);\n"
    
    def GetStructName(self):
        return underline_to_camel(self.tablename)
    
    def GetFieldsFmt(self):
        fields_fmt = []
        for field in self:
            fields_fmt.append(field.GetFormat())
        return fields_fmt
    
    def GetFieldsType(self):
        fields_type = []
        for field in self:
            fields_type.append(FieldType(field.GetName(), field.GetType(), field.GetComment()))
        return fields_type
    
    def BuildInsertSql(self):
        fields_fmt = self.GetFieldsFmt()
        sql = "insert into " + self.tablename + " ("
        for field_fmt in fields_fmt:
            sql += field_fmt.GetName()
            sql += ", "
        sql = sql.strip(", ")
        sql += ") values ("
        for field_fmt in fields_fmt:
            sql += field_fmt.GetFmt()
            sql += ", "
        sql = sql.strip(", ")
        sql += ")"
        return sql
    
    def BuildFuncStatement(self):
        
        return   "\tstatic void Init (LogManager* m_pLogMgr);\n" \
               + "\tvirtual std::string BuildInsertSql() const;\n"
    
    def BuildFuncBody(self):
        func_body = "LLong " + self.GetStructName() + "::id = 0;\n\n"
        
        func_body += "void " + self.GetStructName() + "::Init (LogManager* pLogMgr) {\n";
        func_body += '\tid = pLogMgr->LoadLogSeq("' + self.GetTableName() + '" );\n'
        func_body += "}\n\n"
    
        func_body += "std::string " + self.GetStructName() + "::BuildInsertSql()const {\n"
        func_body += '\tchar sql[2048];\n'
        func_body += '\tsnprintf(sql, 2047, "' + self.BuildInsertSql() + '",\n';
        for field in self:
            if "id" == field.GetName() :
                func_body += "++" + field.GetParam() + ", "
            else:
                func_body += field.GetParam() + ", "
                
        func_body = func_body.strip(", ")
        func_body += ");\n"
        func_body += "\treturn std::string(sql);\n"
        func_body += "}\n\n"
        
#         func_body += "const std::string& " + self.GetStructName() + "::GetTableName()const {\n"
#         func_body += "\treturn table;\n"
#         func_body += "}\n\n"
        
        return func_body
        
    def BuildStruct(self):
        struct_body = "//" + self.comment + "\n"
        struct_body += "class " + self.GetStructName() + " : public LogStruct {\npublic:\n"
        struct_body += self.BuildFuncStatement()
        struct_body += "\n"
        for field_type in self.GetFieldsType():
            
            if "id" == field_type.GetName():
                struct_body += "private:\n"
                struct_body += "\t"
                struct_body += "static "
                struct_body += field_type.GetType()
                struct_body += "\t"
                struct_body += field_type.GetName()
                struct_body += ";//"
                struct_body += field_type.GetComment() + "\n\n"
                struct_body += "public:\n"
            else: 
                struct_body += "\t"
                struct_body += field_type.GetType()
                struct_body += "\t"
                struct_body += field_type.GetName()
                struct_body += ";//"
                struct_body += field_type.GetComment() + "\n"
                
        struct_body += "};\n"
        return struct_body
       
    def BuildCreateSql(self): 
        sql = "CREATE TABLE IF NOT EXISTS `" + self.tablename + "` (\n";
        for field in self:
            sql += "`" + field.GetName() + "` " + field.GetCreateType() + " NOT NULL ,\n"
            if field.GetComment().find("主键") >= 0 :
                sql += "PRIMARY KEY (`" + field.GetName() + "`),\n"
        sql = sql.strip(",\n")
        sql += ");"
        return sql   
        
    def __repr__(self):
        s = self.tablename + "\n"
        for field in self:
            s += field.__str__()
        return s
    
    __str__ = __repr__
    
class LoadTable(object):
    def __init__(self, filename):
        self.filename = filename
        self.tables = []
    
    def Load(self):
        for line in open(self.filename):
            line = line.strip('\n')                     #去掉换行符
            line = line.strip()                         #去掉两端的空格
            if line :                                     
                attrs = line.split()                    #以空格来分割字符串
            
                if 2 == len(attrs):                     #列表长度1为表格名称
                    table = Table(attrs[1], attrs[0])   #创建表格
                elif len(attrs) >= 4:                                   #否则为表格字段                        
                    table.AddField(Field(attrs))        #在表中添加字段
                else:
                    print "invalid field\n"
            else:
                if table:
                    self.tables.append(table)            #添加表
                    table = None
        if table :
            self.tables.append(table)            #添加表
                
    
    def BuildInsertSql (self):
        for table in self.tables:
            print '%s\n' %(table.BuildInsertSql())
            
    def BuildStruct(self):
        for table in self.tables:
            print "%s\n" %(table.BuildStruct())
    
    def BuildFunc(self):
        for table in self.tables:
            print "%s\n" %(table.BuildFuncBody())
    
    def BuildCreateSql(self):
        for table in self.tables:
            print "%s\n" %(table.BuildCreateSql())    
    
    def ShowTableDesc(self):
        for table in self.tables:
            print "%s\t%s\n" %(table.GetTableName(), table.GetTableComment())
    
    def ShowCallInit(self):
        for table in self.tables:
            print table.ShowCallInit()
                    
    def __repr__(self):
        s = ""
        for table in self.tables:
            s += table.__str__()
            s += "\n"
        return s
    
    __str__ = __repr__
                
        
def Help():
    print "=====================\n"
    print "s         =       申明\n"
    print "i         =       实现\n"
    print "c         =       创建\n"
    print "d         =       描述\n"
    print "a         =       调用\n"
    print "e         =       退出\n"
    print "=====================\n"
    return raw_input().strip().lower()
           
def main(script, *args):
    load_table = LoadTable("log.txt")
    load_table.Load()
    cmd = Help()
    while 'e' != cmd:
        if 's' == cmd:
            print load_table.BuildStruct()
        elif 'i' == cmd:
            print load_table.BuildFunc()
        elif 'c' == cmd:
            print load_table.BuildCreateSql()
        elif 'd' == cmd:
            print load_table.ShowTableDesc()
        elif 'a' == cmd:
            print load_table.ShowCallInit()
        else:
            print "unkown cmd!\n"
        cmd = Help()
        

if __name__ == '__main__':
    import sys
    main(*sys.argv)  
