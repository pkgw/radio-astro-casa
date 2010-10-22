
/*
 * ALMA - Atacama Large Millimeter Array
 * (c) European Southern Observatory, 2002
 * (c) Associated Universities Inc., 2002
 * Copyright by ESO (in the framework of the ALMA collaboration),
 * Copyright by AUI (in the framework of the ALMA collaboration),
 * All rights reserved.
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY, without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston,
 * MA 02111-1307  USA
 *
 * Warning!
 *  -------------------------------------------------------------------- 
 * | This is generated code!  Do not modify this file.                  |
 * | If you do, all changes will be lost when the file is re-generated. |
 *  --------------------------------------------------------------------
 *
 * File ProcessorRow.h
 */
 
#ifndef ProcessorRow_CLASS
#define ProcessorRow_CLASS

#include <vector>
#include <string>
#include <set>
using std::vector;
using std::string;
using std::set;

#ifndef WITHOUT_ACS
#include <asdmIDLC.h>
using asdmIDL::ProcessorRowIDL;
#endif






#include <Tag.h>
using  asdm::Tag;




	

	

	
#include "CProcessorType.h"
using namespace ProcessorTypeMod;
	

	
#include "CProcessorSubType.h"
using namespace ProcessorSubTypeMod;
	



#include <ConversionException.h>
#include <NoSuchRow.h>
#include <IllegalAccessException.h>


/*\file Processor.h
    \brief Generated from model's revision "1.55", branch "HEAD"
*/

namespace asdm {

//class asdm::ProcessorTable;

	

class ProcessorRow;
typedef void (ProcessorRow::*ProcessorAttributeFromBin) (EndianISStream& eiss);

/**
 * The ProcessorRow class is a row of a ProcessorTable.
 * 
 * Generated from model's revision "1.55", branch "HEAD"
 *
 */
class ProcessorRow {
friend class asdm::ProcessorTable;

public:

	virtual ~ProcessorRow();

	/**
	 * Return the table to which this row belongs.
	 */
	ProcessorTable &getTable() const;
	
	/**
	 * Has this row been added to its table ?
	 * @return true if and only if it has been added.
	 */
	bool isAdded() const;
		
	////////////////////////////////
	// Intrinsic Table Attributes //
	////////////////////////////////
	
	
	// ===> Attribute processorId
	
	
	

	
 	/**
 	 * Get processorId.
 	 * @return processorId as Tag
 	 */
 	Tag getProcessorId() const;
	
 
 	
 	
	
	


	
	// ===> Attribute modeId
	
	
	

	
 	/**
 	 * Get modeId.
 	 * @return modeId as Tag
 	 */
 	Tag getModeId() const;
	
 
 	
 	
 	/**
 	 * Set modeId with the specified Tag.
 	 * @param modeId The Tag value to which modeId is to be set.
 	 
 		
 			
 	 */
 	void setModeId (Tag modeId);
  		
	
	
	


	
	// ===> Attribute processorType
	
	
	

	
 	/**
 	 * Get processorType.
 	 * @return processorType as ProcessorTypeMod::ProcessorType
 	 */
 	ProcessorTypeMod::ProcessorType getProcessorType() const;
	
 
 	
 	
 	/**
 	 * Set processorType with the specified ProcessorTypeMod::ProcessorType.
 	 * @param processorType The ProcessorTypeMod::ProcessorType value to which processorType is to be set.
 	 
 		
 			
 	 */
 	void setProcessorType (ProcessorTypeMod::ProcessorType processorType);
  		
	
	
	


	
	// ===> Attribute processorSubType
	
	
	

	
 	/**
 	 * Get processorSubType.
 	 * @return processorSubType as ProcessorSubTypeMod::ProcessorSubType
 	 */
 	ProcessorSubTypeMod::ProcessorSubType getProcessorSubType() const;
	
 
 	
 	
 	/**
 	 * Set processorSubType with the specified ProcessorSubTypeMod::ProcessorSubType.
 	 * @param processorSubType The ProcessorSubTypeMod::ProcessorSubType value to which processorSubType is to be set.
 	 
 		
 			
 	 */
 	void setProcessorSubType (ProcessorSubTypeMod::ProcessorSubType processorSubType);
  		
	
	
	


	////////////////////////////////
	// Extrinsic Table Attributes //
	////////////////////////////////
	
	///////////
	// Links //
	///////////
	
	
	
	
	/**
	 * Compare each mandatory attribute except the autoincrementable one of this ProcessorRow with 
	 * the corresponding parameters and return true if there is a match and false otherwise.
	 	
	 * @param modeId
	    
	 * @param processorType
	    
	 * @param processorSubType
	    
	 */ 
	bool compareNoAutoInc(Tag modeId, ProcessorTypeMod::ProcessorType processorType, ProcessorSubTypeMod::ProcessorSubType processorSubType);
	
	

	
	/**
	 * Compare each mandatory value (i.e. not in the key) attribute  with 
	 * the corresponding parameters and return true if there is a match and false otherwise.
	 	
	 * @param modeId
	    
	 * @param processorType
	    
	 * @param processorSubType
	    
	 */ 
	bool compareRequiredValue(Tag modeId, ProcessorTypeMod::ProcessorType processorType, ProcessorSubTypeMod::ProcessorSubType processorSubType); 
		 
	
	/**
	 * Return true if all required attributes of the value part are equal to their homologues
	 * in x and false otherwise.
	 *
	 * @param x a pointer on the ProcessorRow whose required attributes of the value part 
	 * will be compared with those of this.
	 * @return a boolean.
	 */
	bool equalByRequiredValue(ProcessorRow* x) ;
	
#ifndef WITHOUT_ACS
	/**
	 * Return this row in the form of an IDL struct.
	 * @return The values of this row as a ProcessorRowIDL struct.
	 */
	ProcessorRowIDL *toIDL() const;
#endif
	
#ifndef WITHOUT_ACS
	/**
	 * Fill the values of this row from the IDL struct ProcessorRowIDL.
	 * @param x The IDL struct containing the values used to fill this row.
	 * @throws ConversionException
	 */
	void setFromIDL (ProcessorRowIDL x) ;
#endif
	
	/**
	 * Return this row in the form of an XML string.
	 * @return The values of this row as an XML string.
	 */
	string toXML() const;

	/**
	 * Fill the values of this row from an XML string 
	 * that was produced by the toXML() method.
	 * @param rowDoc the XML string being used to set the values of this row.
	 * @throws ConversionException
	 */
	void setFromXML (string rowDoc) ;	

private:
	/**
	 * The table to which this row belongs.
	 */
	ProcessorTable &table;
	/**
	 * Whether this row has been added to the table or not.
	 */
	bool hasBeenAdded;

	// This method is used by the Table class when this row is added to the table.
	void isAdded(bool added);


	/**
	 * Create a ProcessorRow.
	 * <p>
	 * This constructor is private because only the
	 * table can create rows.  All rows know the table
	 * to which they belong.
	 * @param table The table to which this row belongs.
	 */ 
	ProcessorRow (ProcessorTable &table);

	/**
	 * Create a ProcessorRow using a copy constructor mechanism.
	 * <p>
	 * Given a ProcessorRow row and a ProcessorTable table, the method creates a new
	 * ProcessorRow owned by table. Each attribute of the created row is a copy (deep)
	 * of the corresponding attribute of row. The method does not add the created
	 * row to its table, its simply parents it to table, a call to the add method
	 * has to be done in order to get the row added (very likely after having modified
	 * some of its attributes).
	 * If row is null then the method returns a row with default values for its attributes. 
	 *
	 * This constructor is private because only the
	 * table can create rows.  All rows know the table
	 * to which they belong.
	 * @param table The table to which this row belongs.
	 * @param row  The row which is to be copied.
	 */
	 ProcessorRow (ProcessorTable &table, ProcessorRow &row);
	 	
	////////////////////////////////
	// Intrinsic Table Attributes //
	////////////////////////////////
	
	
	// ===> Attribute processorId
	
	

	Tag processorId;

	
	
 	
 	/**
 	 * Set processorId with the specified Tag value.
 	 * @param processorId The Tag value to which processorId is to be set.
		
 		
			
 	 * @throw IllegalAccessException If an attempt is made to change this field after is has been added to the table.
 	 		
 	 */
 	void setProcessorId (Tag processorId);
  		
	

	
	// ===> Attribute modeId
	
	

	Tag modeId;

	
	
 	

	
	// ===> Attribute processorType
	
	

	ProcessorTypeMod::ProcessorType processorType;

	
	
 	

	
	// ===> Attribute processorSubType
	
	

	ProcessorSubTypeMod::ProcessorSubType processorSubType;

	
	
 	

	////////////////////////////////
	// Extrinsic Table Attributes //
	////////////////////////////////
	
	///////////
	// Links //
	///////////
	
	
	///////////////////////////////
	// binary-deserialization material//
	///////////////////////////////
	map<string, ProcessorAttributeFromBin> fromBinMethods;
void processorIdFromBin( EndianISStream& eiss);
void modeIdFromBin( EndianISStream& eiss);
void processorTypeFromBin( EndianISStream& eiss);
void processorSubTypeFromBin( EndianISStream& eiss);

		
	
	/**
	 * Serialize this into a stream of bytes written to an EndianOSStream.
	 * @param eoss the EndianOSStream to be written to
	 */
	 void toBin(EndianOSStream& eoss);
	 	 
	 /**
	  * Deserialize a stream of bytes read from an EndianISStream to build a PointingRow.
	  * @param eiss the EndianISStream to be read.
	  * @param table the ProcessorTable to which the row built by deserialization will be parented.
	  * @param attributesSeq a vector containing the names of the attributes . The elements order defines the order 
	  * in which the attributes are written in the binary serialization.
	  */
	 static ProcessorRow* fromBin(EndianISStream& eiss, ProcessorTable& table, const vector<string>& attributesSeq);	 

};

} // End namespace asdm

#endif /* Processor_CLASS */
