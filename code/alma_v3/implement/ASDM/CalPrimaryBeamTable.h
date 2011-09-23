
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
 * File CalPrimaryBeamTable.h
 */
 
#ifndef CalPrimaryBeamTable_CLASS
#define CalPrimaryBeamTable_CLASS

#include <string>
#include <vector>
#include <map>



	
#include <ArrayTime.h>
	

	
#include <Angle.h>
	

	
#include <Tag.h>
	

	
#include <Frequency.h>
	

	
#include <EntityRef.h>
	




	

	
#include "CReceiverBand.h"
	

	

	

	
#include "CAntennaMake.h"
	

	

	

	

	
#include "CPolarizationType.h"
	

	

	

	

	

	

	

	
#include "CPrimaryBeamDescription.h"
	

	

	



#include <ConversionException.h>
#include <DuplicateKey.h>
#include <UniquenessViolationException.h>
#include <NoSuchRow.h>
#include <DuplicateKey.h>


#ifndef WITHOUT_ACS
#include <asdmIDLC.h>
#endif

#include <Representable.h>

namespace asdm {

//class asdm::ASDM;
//class asdm::CalPrimaryBeamRow;

class ASDM;
class CalPrimaryBeamRow;
/**
 * The CalPrimaryBeamTable class is an Alma table.
 * <BR>
 * 
 * \par Role
 * Result of Primary Beam Map measurement.
 * <BR>
 
 * Generated from model's revision "1.60", branch "HEAD"
 *
 * <TABLE BORDER="1">
 * <CAPTION> Attributes of CalPrimaryBeam </CAPTION>
 * <TR BGCOLOR="#AAAAAA"> <TH> Name </TH> <TH> Type </TH> <TH> Expected shape  </TH> <TH> Comment </TH></TR>
 
 * <TR> <TH BGCOLOR="#CCCCCC" colspan="4" align="center"> Key </TD></TR>
	
 * <TR>
 		
 * <TD> antennaName </TD>
 		 
 * <TD> string</TD>
 * <TD> &nbsp; </TD>
 * <TD> &nbsp;the name of the antenna. </TD>
 * </TR>
	
 * <TR>
 		
 * <TD> receiverBand </TD>
 		 
 * <TD> ReceiverBandMod::ReceiverBand</TD>
 * <TD> &nbsp; </TD>
 * <TD> &nbsp;identifies the receiver band. </TD>
 * </TR>
	
 * <TR>
 		
 * <TD> calDataId </TD>
 		 
 * <TD> Tag</TD>
 * <TD> &nbsp; </TD>
 * <TD> &nbsp;refers to a unique row in CalData Table. </TD>
 * </TR>
	
 * <TR>
 		
 * <TD> calReductionId </TD>
 		 
 * <TD> Tag</TD>
 * <TD> &nbsp; </TD>
 * <TD> &nbsp;refers to a unique row in CalReduction Table. </TD>
 * </TR>
	


 * <TR> <TH BGCOLOR="#CCCCCC"  colspan="4" valign="center"> Value <br> (Mandatory) </TH></TR>
	
 * <TR>
 * <TD> startValidTime </TD> 
 * <TD> ArrayTime </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp;the start time of result validity period. </TD>
 * </TR>
	
 * <TR>
 * <TD> endValidTime </TD> 
 * <TD> ArrayTime </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp;the end time of result validity period. </TD>
 * </TR>
	
 * <TR>
 * <TD> antennaMake </TD> 
 * <TD> AntennaMakeMod::AntennaMake </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp;the antenna make. </TD>
 * </TR>
	
 * <TR>
 * <TD> numSubband </TD> 
 * <TD> int </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp;the number of subband images (frequency ranges simultaneously measured ). </TD>
 * </TR>
	
 * <TR>
 * <TD> frequencyRange </TD> 
 * <TD> vector<vector<Frequency > > </TD>
 * <TD>  numSubband, 2 </TD> 
 * <TD> &nbsp;the range of frequencies over which the result is valid. </TD>
 * </TR>
	
 * <TR>
 * <TD> numReceptor </TD> 
 * <TD> int </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp;the number of receptors. </TD>
 * </TR>
	
 * <TR>
 * <TD> polarizationTypes </TD> 
 * <TD> vector<PolarizationTypeMod::PolarizationType > </TD>
 * <TD>  numReceptor </TD> 
 * <TD> &nbsp;identifies the polarizations types of the receptors (one value per receptor). </TD>
 * </TR>
	
 * <TR>
 * <TD> mainBeamEfficiency </TD> 
 * <TD> vector<double > </TD>
 * <TD>  numReceptor </TD> 
 * <TD> &nbsp;the main beam efficiency as derived from the beam map. </TD>
 * </TR>
	
 * <TR>
 * <TD> beamDescriptionUID </TD> 
 * <TD> EntityRef </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp;refers to the beam description image. </TD>
 * </TR>
	
 * <TR>
 * <TD> relativeAmplitudeRms </TD> 
 * <TD> float </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp;the RMS fluctuations in terms of the relative beam amplitude. </TD>
 * </TR>
	
 * <TR>
 * <TD> direction </TD> 
 * <TD> vector<Angle > </TD>
 * <TD>  2 </TD> 
 * <TD> &nbsp;the center direction. </TD>
 * </TR>
	
 * <TR>
 * <TD> minValidDirection </TD> 
 * <TD> vector<Angle > </TD>
 * <TD>  2 </TD> 
 * <TD> &nbsp;the minimum center direction of validity. </TD>
 * </TR>
	
 * <TR>
 * <TD> maxValidDirection </TD> 
 * <TD> vector<Angle > </TD>
 * <TD>  2 </TD> 
 * <TD> &nbsp;the maximum center direction of validity. </TD>
 * </TR>
	
 * <TR>
 * <TD> descriptionType </TD> 
 * <TD> PrimaryBeamDescriptionMod::PrimaryBeamDescription </TD>
 * <TD>  &nbsp;  </TD> 
 * <TD> &nbsp;quantity used to describe beam. </TD>
 * </TR>
	
 * <TR>
 * <TD> imageChannelNumber </TD> 
 * <TD> vector<int > </TD>
 * <TD>  numSubband </TD> 
 * <TD> &nbsp;channel number in image for each subband. </TD>
 * </TR>
	
 * <TR>
 * <TD> imageNominalFrequency </TD> 
 * <TD> vector<Frequency > </TD>
 * <TD>  numSubband </TD> 
 * <TD> &nbsp;nominal frequency for subband. </TD>
 * </TR>
	


 * </TABLE>
 */
class CalPrimaryBeamTable : public Representable {
	friend class ASDM;

public:


	/**
	 * Return the list of field names that make up key key
	 * as an array of strings.
	 * @return a vector of string.
	 */	
	static std::vector<std::string> getKeyName();


	virtual ~CalPrimaryBeamTable();
	
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
	unsigned int size() const;
	
	/**
	 * Return the name of this table.
	 *
	 * @return the name of this table in a string.
	 */
	std::string getName() const;
	
	/**
	 * Return the version information about this table.
	 *
	 */
	 std::string getVersion() const ;
	
	/**
	 * Return the names of the attributes of this table.
	 *
	 * @return a vector of string
	 */
	 static const std::vector<std::string>& getAttributesNames();

	/**
	 * Return this table's Entity.
	 */
	Entity getEntity() const;

	/**
	 * Set this table's Entity.
	 * @param e An entity. 
	 */
	void setEntity(Entity e);
		
	/**
	 * Produces an XML representation conform
	 * to the schema defined for CalPrimaryBeam (CalPrimaryBeamTable.xsd).
	 *
	 * @returns a string containing the XML representation.
	 * @throws ConversionException
	 */
	std::string toXML()  ;

#ifndef WITHOUT_ACS
	// Conversion Methods
	/**
	 * Convert this table into a CalPrimaryBeamTableIDL CORBA structure.
	 *
	 * @return a pointer to a CalPrimaryBeamTableIDL
	 */
	asdmIDL::CalPrimaryBeamTableIDL *toIDL() ;
#endif

#ifndef WITHOUT_ACS
	/**
	 * Populate this table from the content of a CalPrimaryBeamTableIDL Corba structure.
	 *
	 * @throws DuplicateKey Thrown if the method tries to add a row having a key that is already in the table.
	 * @throws ConversionException
	 */	
	void fromIDL(asdmIDL::CalPrimaryBeamTableIDL x) ;
#endif
	
	//
	// ====> Row creation.
	//
	
	/**
	 * Create a new row with default values.
	 * @return a pointer on a CalPrimaryBeamRow
	 */
	CalPrimaryBeamRow *newRow();
	
	
	/**
	 * Create a new row initialized to the specified values.
	 * @return a pointer on the created and initialized row.
	
 	 * @param antennaName
	
 	 * @param receiverBand
	
 	 * @param calDataId
	
 	 * @param calReductionId
	
 	 * @param startValidTime
	
 	 * @param endValidTime
	
 	 * @param antennaMake
	
 	 * @param numSubband
	
 	 * @param frequencyRange
	
 	 * @param numReceptor
	
 	 * @param polarizationTypes
	
 	 * @param mainBeamEfficiency
	
 	 * @param beamDescriptionUID
	
 	 * @param relativeAmplitudeRms
	
 	 * @param direction
	
 	 * @param minValidDirection
	
 	 * @param maxValidDirection
	
 	 * @param descriptionType
	
 	 * @param imageChannelNumber
	
 	 * @param imageNominalFrequency
	
     */
	CalPrimaryBeamRow *newRow(string antennaName, ReceiverBandMod::ReceiverBand receiverBand, Tag calDataId, Tag calReductionId, ArrayTime startValidTime, ArrayTime endValidTime, AntennaMakeMod::AntennaMake antennaMake, int numSubband, vector<vector<Frequency > > frequencyRange, int numReceptor, vector<PolarizationTypeMod::PolarizationType > polarizationTypes, vector<double > mainBeamEfficiency, EntityRef beamDescriptionUID, float relativeAmplitudeRms, vector<Angle > direction, vector<Angle > minValidDirection, vector<Angle > maxValidDirection, PrimaryBeamDescriptionMod::PrimaryBeamDescription descriptionType, vector<int > imageChannelNumber, vector<Frequency > imageNominalFrequency);
	


	/**
	 * Create a new row using a copy constructor mechanism.
	 * 
	 * The method creates a new CalPrimaryBeamRow owned by this. Each attribute of the created row 
	 * is a (deep) copy of the corresponding attribute of row. The method does not add 
	 * the created row to this, its simply parents it to this, a call to the add method
	 * has to be done in order to get the row added (very likely after having modified
	 * some of its attributes).
	 * If row is null then the method returns a new CalPrimaryBeamRow with default values for its attributes. 
	 *
	 * @param row the row which is to be copied.
	 */
	 CalPrimaryBeamRow *newRow(CalPrimaryBeamRow *row); 

	//
	// ====> Append a row to its table.
	//
 
	
	/**
	 * Add a row.
	 * @param x a pointer to the CalPrimaryBeamRow to be added.
	 *
	 * @return a pointer to a CalPrimaryBeamRow. If the table contains a CalPrimaryBeamRow whose attributes (key and mandatory values) are equal to x ones
	 * then returns a pointer on that CalPrimaryBeamRow, otherwise returns x.
	 *
	 * @throw DuplicateKey { thrown when the table contains a CalPrimaryBeamRow with a key equal to the x one but having
	 * and a value section different from x one }
	 *
	
	 */
	CalPrimaryBeamRow* add(CalPrimaryBeamRow* x) ; 

 



	//
	// ====> Methods returning rows.
	//
		
	/**
	 * Get a collection of pointers on the rows of the table.
	 * @return Alls rows in a vector of pointers of CalPrimaryBeamRow. The elements of this vector are stored in the order 
	 * in which they have been added to the CalPrimaryBeamTable.
	 */
	std::vector<CalPrimaryBeamRow *> get() ;
	
	/**
	 * Get a const reference on the collection of rows pointers internally hold by the table.
	 * @return A const reference of a vector of pointers of CalPrimaryBeamRow. The elements of this vector are stored in the order 
	 * in which they have been added to the CalPrimaryBeamTable.
	 *
	 */
	 const std::vector<CalPrimaryBeamRow *>& get() const ;
	


 
	
	/**
 	 * Returns a CalPrimaryBeamRow* given a key.
 	 * @return a pointer to the row having the key whose values are passed as parameters, or 0 if
 	 * no row exists for that key.
	
	 * @param antennaName
	
	 * @param receiverBand
	
	 * @param calDataId
	
	 * @param calReductionId
	
 	 *
	 */
 	CalPrimaryBeamRow* getRowByKey(string antennaName, ReceiverBandMod::ReceiverBand receiverBand, Tag calDataId, Tag calReductionId);

 	 	



	/**
 	 * Look up the table for a row whose all attributes 
 	 * are equal to the corresponding parameters of the method.
 	 * @return a pointer on this row if any, null otherwise.
 	 *
			
 	 * @param antennaName
 	 		
 	 * @param receiverBand
 	 		
 	 * @param calDataId
 	 		
 	 * @param calReductionId
 	 		
 	 * @param startValidTime
 	 		
 	 * @param endValidTime
 	 		
 	 * @param antennaMake
 	 		
 	 * @param numSubband
 	 		
 	 * @param frequencyRange
 	 		
 	 * @param numReceptor
 	 		
 	 * @param polarizationTypes
 	 		
 	 * @param mainBeamEfficiency
 	 		
 	 * @param beamDescriptionUID
 	 		
 	 * @param relativeAmplitudeRms
 	 		
 	 * @param direction
 	 		
 	 * @param minValidDirection
 	 		
 	 * @param maxValidDirection
 	 		
 	 * @param descriptionType
 	 		
 	 * @param imageChannelNumber
 	 		
 	 * @param imageNominalFrequency
 	 		 
 	 */
	CalPrimaryBeamRow* lookup(string antennaName, ReceiverBandMod::ReceiverBand receiverBand, Tag calDataId, Tag calReductionId, ArrayTime startValidTime, ArrayTime endValidTime, AntennaMakeMod::AntennaMake antennaMake, int numSubband, vector<vector<Frequency > > frequencyRange, int numReceptor, vector<PolarizationTypeMod::PolarizationType > polarizationTypes, vector<double > mainBeamEfficiency, EntityRef beamDescriptionUID, float relativeAmplitudeRms, vector<Angle > direction, vector<Angle > minValidDirection, vector<Angle > maxValidDirection, PrimaryBeamDescriptionMod::PrimaryBeamDescription descriptionType, vector<int > imageChannelNumber, vector<Frequency > imageNominalFrequency); 


	void setUnknownAttributeBinaryReader(const std::string& attributeName, BinaryAttributeReaderFunctor* barFctr);
	BinaryAttributeReaderFunctor* getUnknownAttributeBinaryReader(const std::string& attributeName) const;

private:

	/**
	 * Create a CalPrimaryBeamTable.
	 * <p>
	 * This constructor is private because only the
	 * container can create tables.  All tables must know the container
	 * to which they belong.
	 * @param container The container to which this table belongs.
	 */ 
	CalPrimaryBeamTable (ASDM & container);

	ASDM & container;
	
	bool archiveAsBin; // If true archive binary else archive XML
	bool fileAsBin ; // If true file binary else file XML	
	
	std::string version ; 
	
	Entity entity;
	


	/**
	 * The name of this table.
	 */
	static std::string tableName;
	
	/**
	 * The attributes names.
	 */
	static const std::vector<std::string> attributesNames;
	
	/**
	 * A method to fill attributesNames;
	 */
	static std::vector<std::string> initAttributesNames();


	/**
	 * The list of field names that make up key key.
	 */
	static std::vector<std::string> key;


	/**
	 * If this table has an autoincrementable attribute then check if *x verifies the rule of uniqueness and throw exception if not.
	 * Check if *x verifies the key uniqueness rule and throw an exception if not.
	 * Append x to its table.
	 * @throws DuplicateKey
	 
	 */
	CalPrimaryBeamRow* checkAndAdd(CalPrimaryBeamRow* x) ;
	
	/**
	 * Brutally append an CalPrimaryBeamRow x to the collection of rows already stored in this table. No uniqueness check is done !
	 *
	 * @param CalPrimaryBeamRow* x a pointer onto the CalPrimaryBeamRow to be appended.
	 */
	 void append(CalPrimaryBeamRow* x) ;
	 
	 



// A data structure to store the pointers on the table's rows.

// In all cases we maintain a private vector of CalPrimaryBeamRow s.
   std::vector<CalPrimaryBeamRow * > privateRows;
   

			
	std::vector<CalPrimaryBeamRow *> row;

	
	void error() ; //throw(ConversionException);

	
	/**
	 * Populate this table from the content of a XML document that is required to
	 * be conform to the XML schema defined for a CalPrimaryBeam (CalPrimaryBeamTable.xsd).
	 * @throws ConversionException
	 * 
	 */
	void fromXML(std::string& xmlDoc) ;
		
	std::map<std::string, BinaryAttributeReaderFunctor *> unknownAttributes2Functors;

	/**
	  * Private methods involved during the build of this table out of the content
	  * of file(s) containing an external representation of a CalPrimaryBeam table.
	  */
	void setFromMIMEFile(const std::string& directory);
	void setFromXMLFile(const std::string& directory);
	
		 /**
	 * Serialize this into a stream of bytes and encapsulates that stream into a MIME message.
	 * @returns a string containing the MIME message.
	 *
	 * @param byteOrder a const pointer to a static instance of the class ByteOrder.
	 * 
	 */
	std::string toMIME(const asdm::ByteOrder* byteOrder=asdm::ByteOrder::Machine_Endianity);
  
	
   /** 
     * Extracts the binary part of a MIME message and deserialize its content
	 * to fill this with the result of the deserialization. 
	 * @param mimeMsg the string containing the MIME message.
	 * @throws ConversionException
	 */
	 void setFromMIME(const std::string & mimeMsg);
	
	/**
	  * Private methods involved during the export of this table into disk file(s).
	  */
	std::string MIMEXMLPart(const asdm::ByteOrder* byteOrder=asdm::ByteOrder::Machine_Endianity);
	
	/**
	  * Stores a representation (binary or XML) of this table into a file.
	  *
	  * Depending on the boolean value of its private field fileAsBin a binary serialization  of this (fileAsBin==true)  
	  * will be saved in a file "CalPrimaryBeam.bin" or an XML representation (fileAsBin==false) will be saved in a file "CalPrimaryBeam.xml".
	  * The file is always written in a directory whose name is passed as a parameter.
	 * @param directory The name of directory  where the file containing the table's representation will be saved.
	  * 
	  */
	  void toFile(std::string directory);
	  
	  /**
	   * Load the table in memory if necessary.
	   */
	  bool loadInProgress;
	  void checkPresenceInMemory() {
		if (!presentInMemory && !loadInProgress) {
			loadInProgress = true;
			setFromFile(getContainer().getDirectory());
			presentInMemory = true;
			loadInProgress = false;
	  	}
	  }
	/**
	 * Reads and parses a file containing a representation of a CalPrimaryBeamTable as those produced  by the toFile method.
	 * This table is populated with the result of the parsing.
	 * @param directory The name of the directory containing the file te be read and parsed.
	 * @throws ConversionException If any error occurs while reading the 
	 * files in the directory or parsing them.
	 *
	 */
	 void setFromFile(const std::string& directory);	
 
};

} // End namespace asdm

#endif /* CalPrimaryBeamTable_CLASS */
