from pyasm.coff import coffFile, coffSection, coffRelocationEntry, coffSymbolEntry
from pyasm.coffConst import *
import time

class CpToCoff:
    def __init__(self,cp):
        self.cp = cp
        
        c = coffFile()
        c.MachineType = coffFile.I386MAGIC

        self.coff = c        
        
    def linkDirectiveSection(self, directives="-defaultlib: LIBC -defaultlib:OLDNAMES "):
        sect = coffSection()
        sect.Name = '.drectve'
        sect.Flages = Flags = (SectionFlags.LNK_REMOVE |
                    SectionFlags.LNK_INFO |
                    SectionFlags.ALIGN_1BYTES)
        sect.RawData = directives
        return sect

    def textSection(self):
        sect = coffSection()
        sect.Name = '.text\x00\x00\x00'
        sect.Flags = (SectionFlags.CNT_CODE |
                    SectionFlags.LNK_COMDAT |
                    SectionFlags.MEM_EXECUTE |
                    SectionFlags.MEM_READ |
                    SectionFlags.ALIGN_16BYTES)
        sect.RawData = self.cp.Code

        for patching in self.cp.CodePatchins:
            # How do I tell what type it is?
            r = coffRelocationEntry(addr=0x1,sym=0xC,typ=RelocationTypes.I386_DIR32)
            sect.RelocationData.append(r)

        return sect        

    def dataSection(self):
        sect = coffSection()
        sect.Name = '.data\x00\x00\x00'
        sect.Flags = (SectionFlags.LNK_COMDAT |
                    SectionFlags.CNT_INITIALIZED_DATA |
                    SectionFlags.MEM_WRITE |
                    SectionFlags.MEM_READ |
                    SectionFlags.ALIGN_4BYTES)
        sect.RawData = self.cp.Data
        return sect
        
    def debugF_Section(self):
        "What the hell is this?"
        pass
##        s4=coffSection()
##        s4.Name = '.debug$F'
##        s4.Flags = (SectionFlags.LNK_COMDAT |
##                    SectionFlags.TYPE_NO_PAD |
##                    SectionFlags.CNT_INITIALIZED_DATA |
##                    SectionFlags.MEM_DISCARDABLE |
##                    SectionFlags.MEM_READ |
##                    SectionFlags.ALIGN_1BYTES)
##        s4.RawData = '\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00'
##
##        r = coffRelocationEntry(addr=0x0,sym=0x8,typ=RelocationTypes.I386_DIR32NB)
##        s4.RelocationData.append(r)
##
##        c.Sections.append(s4)

    def addSymbol(self,name,val,sec,typ,cls,aux=''):
        s = coffSymbolEntry(name,val,sec,typ,cls)
        ssAuxiliaries = aux
        self.coff.Symbols.append(s)
        
    def addSymbols(self):
        self.addSymbol('.file\x00\x00\x00',SymbolValues.SYM_UNDEFINED,-2,
                            SymbolTypes.NULL, SymbolClass.CLASS_FILE,
                       'C:\\objtest\\objtest\\objtest.cpp\x00\x00\x00\x00\x00\x00')
        
        self.addSymbol('@comp.id',0xB2306, -1, SymbolTypes.NULL, SymbolClass.STATIC)

        self.addSymbol('.drectve', SymbolValues.SYM_UNDEFINED, 1, SymbolTypes.NULL,
                            SymbolClass.STATIC,
                       '&\x00\x00\x00\x00\x00\x00\x00O\xe0\xad\x98\x00\x00\x00\x00\x00\x00')

        self.addSymbol('.text\x00\x00\x00', SymbolValues.SYM_UNDEFINED, 2,
                            SymbolTypes.NULL, SymbolClass.STATIC)
        #Auxiliaries = "\x10\x00\x00\x00\x02\x00\x00\x00\x9d\xf0\xcd3\x00\x00\x01\x00\x00\x00"


        for sym in self.cp.CodeSymbols:
            self.addSymbol('_main\x00\x00\x00', SymbolValues.SYM_UNDEFINED, 2, 0x20,
                                SymbolClass.EXTERNAL)
 

        self.addSymbol('.data\x00\x00\x00', SymbolValues.SYM_UNDEFINED, 3,
                            SymbolTypes.NULL, SymbolClass.STATIC,
                       '\x0e\x00\x00\x00\x00\x00\x00\x00\xfe,\xa6\xfb\x00\x00\x02\x00\x00\x00')

        self.addSymbol('\x00\x00\x00\x00\x04\x00\x00\x00', SymbolValues.SYM_UNDEFINED, 3,
                            SymbolTypes.NULL, SymbolClass.EXTERNAL)

        self.addSymbol('.debug$F', SymbolValues.SYM_UNDEFINED, 4, SymbolTypes.NULL,
                            SymbolClass.STATIC,
                       '\x10\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x05\x00\x00\x00')



        
    def makeReleaseCoff(self):
        """
        converts a generic codePackage to a coff object
        """
        self.addSymbols()
        
        self.coff.Sections.append(self.linkDirectiveSection())
        self.coff.Sections.append(self.textSection())
        self.coff.Sections.append(self.dataSection())
        #Do Debug$F after we figure out how it works
        #c.Sections.append(self.DebugF_Section())


        self.coff.StringTable = '??_C@_0O@FEEI@Hello?5World?$CB?6?$AA@\x00'

        self.coff.SetSizes()
        self.coff.SetOffsets()

        return self.coff
