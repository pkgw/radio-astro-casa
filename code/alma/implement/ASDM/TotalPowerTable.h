
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
 * File TotalPowerTable.h
 */
 
#ifndef TotalPowerTable_CLASS
#define TotalPowerTable_CLASS

#include <string>
#include <vector>
#include <map>
#include <set>
using std::string;
using std::vector;
using std::map;



#include <ArrayTime.h>
using  asdm::ArrayTime;

#include <Interval.h>
using  asdm::Interval;

#include <Tag.h>
using  asdm::Tag;

#include <Length.h>
using  asdm::Length;




	

	

	

	

	

	

	

	

	

	

	

	

	



#include <ConversionException.h>
#include <DuplicateKey.h>
#include <UniquenessViolationException.h>
#include <NoSuchRow.h>
#include <DuplicateKey.h>
using asdm::DuplicateKey;
using asdm::ConversionException;
using asdm::NoSuchRow;
using asdm::DuplicateKey;

#ifndef WITHOUT_ACS
#include <asdmIDLC.h>
using asdmIDL::TotalPowerTableIDL;
#endif

#include <Representable.h>

namespace asdm {

//class asdm::ASDM;
//class asdm::TotalPowerRow;

class ASDM;
class TotalPowerRow;
/**
 * The TotalPowerTable class is an Alma table.
 * <BR>
 * 
 * \par Role
 * Total power data monitoring.
 * <BR>
 
 * Generated from model's revision "1.53", branch "HEAD"
 *
 * <TABLE BORDER="1">
 * <CAPTION> Attributes of TotalPower </CAPTION>
 * <TR BGCOLOR="#AAAAAA"> <TH> Name </TH> <TH> Type </TH> <TH> Expected shape  </TH> <TH> Comment </TH></TR>
 
 * <TR> <TH BGCOLOR="#CCCCCC" colspan="4" align="center"> Key </TD></TR>
	
 * <TR>
 		
 * <TD> time </TD>
 		 
 * <TD> ArrayTime</TD>
 * <TD> &nbsp; </TD>
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 		
 * <TD> configDescriptionId </TD>
 		 
 * <TD> Tag</TD>
 * <TD> &nbsp; </TD>
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 		
 * <TD> fieldId </TD>
 		 
 * <TD> Tag</TD>
 * <TD> &nbsp; </TD>
 * <TD> &nbsp; </TD>
 * </TR>
	


 * <TR> <TH BGCOLOR="#CCCCCC"  colspan="4" valign="center"> Value <br> (Mandarory) </TH></TR>
	
 * <TR>
 * <TD> scanNumber </TD> 
 * <TD> int </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> subscanNumber </TD> 
 * <TD> int </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> integrationNumber </TD> 
 * <TD> int </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> uvw </TD> 
 * <TD> vector<vector<Length > > </TD>
 * <TD>  ConfigDescription.numAntenna, 3 </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> exposure </TD> 
 * <TD> vector<vector<Interval > > </TD>
 * <TD>  ConfigDescription.numAntenna, CorrelatorMode.numBaseband </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> timeCentroid </TD> 
 * <TD> vector<vector<ArrayTime > > </TD>
 * <TD>  ConfigDescription.numAntenna, CorrelatorMode.numBaseband </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> floatData </TD> 
 * <TD> vector<vector<vector<float > > > </TD>
 * <TD>  , ,  </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> flagAnt </TD> 
 * <TD> vector<int > </TD>
 * <TD>  ConfigDescription.numAntenna </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> flagPol </TD> 
 * <TD> vector<vector<int > > </TD>
 * <TD>  ,  </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> flagRow </TD> 
 * <TD> bool </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> interval </TD> 
 * <TD> Interval </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> stateId </TD> 
 * <TD> vector<Tag>  </TD>
 * <TD>  ConfigDescription.numAntenna </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	
 * <TR>
 * <TD> execBlockId </TD> 
 * <TD> Tag </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp; </TD>
 * </TR>
	


 * <TR> <TH BGCOLOR="#CCCCCC"  colspan="4" valign="center"> Value <br> (Optional) </TH></TR>
	
 * <TR>
 * <TD> subintegrationNumber </TD> 
 * <TD> int </TD>
 * <TD>  &nbsp; </TD>
 * <TD>&nbsp;  </TD>
 * </TR>
	

 * </TABLE>
 */
class TotalPowerTable : public Representable {
	friend class ASDM;

public:


	/**
	 * Return the list of field names that make up key key
	 * as an array of strings.
	 * @return a vector of string.
	 */	
	static vector<string> getKeyName();


	virtual ~TotalPowerTable();
	
	/**
	 * Return the container to which this table belongs.
	 *
	 * @return the ASDM containing this table.
	 */
	ASDM &getContainer() const;
	
	/**
	 * Return the number of rows in the table.
	 *
	 * @return the number of rows in an unsigned int.
	 */
	unsigned int size() ;
	
	/**
	 * Return the name of this table.
	 *
	 * @return the name of this table in a string.
	 */
	string getName() const;


	//
	// ====> Row creation.
	//
	
	/**
	 * Create a new row with default values.
	 * @return a pointer on a TotalPowerRow
	 */
	TotalPowerRow *newRow();
	
	
	/**
	 * Create a new row initialized to the specified values.
	 * @return a pointer on the created and initialized row.
	
 	 * @param time
	
 	 * @param configDescriptionId
	
 	 * @param fieldId
	
 	 * @param scanNumber
	
 	 * @param subscanNumber
	
 	 * @param integrationNumber
	
 	 * @param uvw
	
 	 * @param exposure
	
 	 * @param timeCentroid
	
 	 * @param floatData
	
 	 * @param flagAnt
	
 	 * @param flagPol
	
 	 * @param flagRow
	
 	 * @param interval
	
 	 * @param stateId
	
 	 * @param execBlockId
	
     */
	TotalPowerRow *newRow(ArrayTime time, Tag configDescriptionId, Tag fieldId, int scanNumber, int subscanNumber, int integrationNumber, vector<vector<Length > > uvw, vector<vector<Interval > > exposure, vector<vector<ArrayTime > > timeCentroid, vector<vector<vector<float > > > floatData, vector<int > flagAnt, vector<vector<int > > flagPol, bool flagRow, Interval interval, vector<Tag>  stateId, Tag execBlockId);
	


	/**
	 * Create a new row using a copy constructor mechanism.
	 * 
	 * The method creates a new TotalPowerRow owned by this. Each attribute of the created row 
	 * is a (deep) copy of the corresponding attribute of row. The method does not add 
	 * the created row to this, its simply parents it to this, a call to the add method
	 * has to be done in order to get the row added (very likely after having modified
	 * some of its attributes).
	 * If row is null then the method returns a new TotalPowerRow with default values for its attributes. 
	 *
	 * @param row the row which is to be copied.
	 */
	 TotalPowerRow *newRow(TotalPowerRow *row); 

	//
	// ====> Append a row to its table.
	//
 
	
	/**
	 * Add a row.
	 * @param x a pointer to the TotalPowerRow to be added.
	 *
	 * @return a pointer to a TotalPowerRow. If the table contains a TotalPowerRow whose attributes (key and mandatory values) are equal to x ones
	 * then returns a pointer on that TotalPowerRow, otherwise returns x.
	 *
	 * @throw DuplicateKey { thrown when the table contains a TotalPowerRow with a key equal to the x one but having
	 * and a value section different from x one }
	 *
	
	 * @note The row is inserted in the table in such a way that all the rows having the same value of
	 * ( configDescriptionId, fieldId ) are stored by ascending time.
	 * @see method getByContext.
	
	 */
	TotalPowerRow* add(TotalPowerRow* x) ; 

 



	//
	// ====> Methods returning rows.
	//
		
	/**
	 * Get all rows.
	 * @return Alls rows as a vector of pointers of TotalPowerRow. The elements of this vector are stored in the order 
	 * in which they have been added to the TotalPowerTable.
	 */
	vector<TotalPowerRow *> get() ;
	

	/**
	 * Returns all the rows sorted by ascending startTime for a given context. 
	 * The context is defined by a value of ( configDescriptionId, fieldId ).
	 *
	 * @return a pointer on a vector<TotalPowerRow *>. A null returned value means that the table contains
	 * no TotalPowerRow for the given ( configDescriptionId, fieldId ).
	 */
	 vector <TotalPowerRow*> *getByContext(Tag configDescriptionId, Tag fieldId);
	 


 
	
	/**
 	 * Returns a TotalPowerRow* given a key.
 	 * @return a pointer to the row having the key whose values are passed as parameters, or 0 if
 	 * no row exists for that key.
	
	 * @param time
	
	 * @param configDescriptionId
	
	 * @param fieldId
	
 	 *
	 */
 	TotalPowerRow* getRowByKey(ArrayTime time, Tag configDescriptionId, Tag fieldId);

 	 	



	/**
 	 * Look up the table for a row whose all attributes 
 	 * are equal to the corresponding parameters of the method.
 	 * @return a pointer on this row if any, null otherwise.
 	 *
			
 	 * @param time
 	 		
 	 * @param configDescriptionId
 	 		
 	 * @param fieldId
 	 		
 	 * @param scanNumber
 	 		
 	 * @param subscanNumber
 	 		
 	 * @param integrationNumber
 	 		
 	 * @param uvw
 	 		
 	 * @param exposure
 	 		
 	 * @param timeCentroid
 	 		
 	 * @param floatData
 	 		
 	 * @param flagAnt
 	 		
 	 * @param flagPol
 	 		
 	 * @param flagRow
 	 		
 	 * @param interval
 	 		
 	 * @param stateId
 	 		
 	 * @param execBlockId
 	 		 
 	 */
	TotalPowerRow* lookup(ArrayTime time, Tag configDescriptionId, Tag fieldId, int scanNumber, int subscanNumber, int integrationNumber, vector<vector<Length > > uvw, vector<vector<Interval > > exposure, vector<vector<ArrayTime > > timeCentroid, vector<vector<vector<float > > > floatData, vector<int > flagAnt, vector<vector<int > > flagPol, bool flagRow, Interval interval, vector<Tag>  stateId, Tag execBlockId); 


private:

	/**
	 * Create a TotalPowerTable.
	 * <p>
	 * This constructor is private because only the
	 * container can create tables.  All tables must know the container
	 * to which they belong.
	 * @param container The container to which this table belongs.
	 */ 
	TotalPowerTable (ASDM & container);

	ASDM & container;
	
	bool archiveAsBin; // If true archive binary else archive XML
	bool fileAsBin ; // If true file binary else file XML	
	
	Entity entity;
	


	/**
	 * The name of this table.
	 */
	static string tableName;


	/**
	 * The list of field names that make up key key.
	 */
	static vector<string> key;


	/**
	 * If this table has an autoincrementable attribute then check if *x verifies the rule of uniqueness and throw exception if not.
	 * Check if *x verifies the key uniqueness rule and throw an exception if not.
	 * Append x to its table.
	 * @throws DuplicateKey
	 
	 */
	TotalPowerRow* checkAndAdd(TotalPowerRow* x) ;


	
   	
   /**
	 * Insert a TotalPowerRow* in a vector of TotalPowerRow* so that it's ordered by ascending time.
	 *
	 * @param TotalPowerRow* x . The pointer to be inserted.
	 * @param vector <TotalPowerRow*>& row . A reference to the vector where to insert x.
	 *
	 */
 	TotalPowerRow * insertByTime(TotalPowerRow* x, vector<TotalPowerRow *>&row );
 	 


// A data structure to store the pointers on the table's rows.

// In all cases we maintain a private vector of TotalPowerRow s.
   vector<TotalPowerRow * > privateRows;
   

	

	
	
		
				
	typedef vector <TotalPowerRow* > TIME_ROWS;
	map<string, TIME_ROWS > context;
		
	/** 
	 * Returns a string built by concatenating the ascii representation of the
	 * parameters values suffixed with a "_" character.
	 */
	 string Key(Tag configDescriptionId, Tag fieldId) ;
		 
		
	
	
	/**
	 * Fills the vector vout (passed by reference) with pointers on elements of vin 
	 * whose attributes are equal to the corresponding parameters of the method.
	 *
	 */
	void getByKeyNoAutoIncNoTime(vector <TotalPowerRow*>& vin, vector <TotalPowerRow*>& vout,  Tag configDescriptionId, Tag fieldId);
	


	/**
	 * Return this table's Entity.
	 */
	Entity getEntity() const;

	/**
	 * Set this table's Entity.
	 * @param e An entity. 
	 */
	void setEntity(Entity e);

#ifndef WITHOUT_ACS
	// Conversion Methods
	/**
	 * Convert this table into a TotalPowerTableIDL CORBA structure.
	 *
	 * @return a pointer to a TotalPowerTableIDL
	 */
	TotalPowerTableIDL *toIDL() ;
#endif

#ifndef WITHOUT_ACS
	/**
	 * Populate this table from the content of a TotalPowerTableIDL Corba structure.
	 *
	 * @throws DuplicateKey Thrown if the method tries to add a row having a key that is already in the table.
	 * @throws ConversionException
	 */	
	void fromIDL(TotalPowerTableIDL x) ;
#endif
	
	
	void error() ; //throw(ConversionException);

	/**
	 * Translate this table to an XML representation conform
	 * to the schema defined for TotalPower (TotalPowerTable.xsd).
	 *
	 * @returns a string containing the XML representation.
	 * @throws ConversionException
	 */
	string toXML()  ;
	
	/**
	 * Populate this table from the content of a XML document that is required to
	 * be conform to the XML schema defined for a TotalPower (TotalPowerTable.xsd).
	 * @throws ConversionException
	 * 
	 */
	void fromXML(string xmlDoc) ;
		
	/**
	  * Private methods involved during the build of this table out of the content
	  * of file(s) containing an external representation of a TotalPower table.
	  */
	void setFromMIMEFile(const string& directory);
	void setFromXMLFile(const string& directory);
	
		 /**
	 * Serialize this into a stream of bytes and encapsulates that stream into a MIME message.
	 * @returns a string containing the MIME message.
	 *
	 * @param byteOrder a const pointer to a static instance of the class ByteOrder.
	 * 
	 */
	string toMIME(const asdm::ByteOrder* byteOrder=asdm::ByteOrder::Machine_Endianity);
  
	
   /** 
     * Extracts the binary part of a MIME message and deserialize its content
	 * to fill this with the result of the deserialization. 
	 * @param mimeMsg the string containing the MIME message.
	 * @throws ConversionException
	 */
	 void setFromMIME(const string & mimeMsg);
	
	/**
	  * Private methods involved during the export of this table into disk file(s).
	  */
	string MIMEXMLPart(const asdm::ByteOrder* byteOrder=asdm::ByteOrder::Machine_Endianity);
	
	/**
	  * Stores a representation (binary or XML) of this table into a file.
	  *
	  * Depending on the boolean value of its private field fileAsBin a binary serialization  of this (fileAsBin==true)  
	  * will be saved in a file "TotalPower.bin" or an XML representation (fileAsBin==false) will be saved in a file "TotalPower.xml".
	  * The file is always written in a directory whose name is passed as a parameter.
	 * @param directory The name of directory  where the file containing the table's representation will be saved.
	  * 
	  */
	  void toFile(string directory);
	  
	/**
	 * Reads and parses a file containing a representation of a TotalPowerTable as those produced  by the toFile method.
	 * This table is populated with the result of the parsing.
	 * @param directory The name of the directory containing the file te be read and parsed.
	 * @throws ConversionException If any error occurs while reading the 
	 * files in the directory or parsing them.
	 *
	 */
	 void setFromFile(const string& directory);	
 
};

} // End namespace asdm

#endif /* TotalPowerTable_CLASS */
