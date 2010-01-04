#if     !defined(ATM_WVRMEASUREMENT_H)

#include "ATMTemperature.h"
#include "ATMLength.h"
#include "ATMAngle.h"
#include <math.h>

namespace atm {
  /*! \brief This is an axuliary class that allows to create objects corresponding 
   *        to measurements (and their analysis) of a multichannel water vapor radiometer system.
   */
  class WVRMeasurement
    {
    public:
      
      /** Class constructor with no radiometric channels */
      WVRMeasurement();
      /** The basic class constructur, with the elevation angle corresponding to the measurement, and the measurements themselves 
          in the channels of the water vapor radiometer system  */
      WVRMeasurement(Angle elevation, vector<Temperature> measuredSkyBrightness);
      /** A more general class constructur, with the elevation angle corresponding to the measurement, the measurements themselves 
          in the channels of the water vapor radiometer system, the fitted values in those channels and the sigma of the fit. This 
          constructor is not intended to be used by the user, but by water vapor retrieval procedures inside the SkyStatus class */
      WVRMeasurement(Angle elevation, vector<Temperature> measuredSkyBrightness, 
		     vector<Temperature> fittedSkyBrightness, 
		     Length retrievedWaterVaporColumn, 
		     Temperature sigma_fittedSkyBrightness);
      
      virtual ~WVRMeasurement();
      
      /** Accessor to elevation */
      Angle getElevation(){return elevation_;}
      /** Accessor to air mass */
      double getAirMass(){return 1.0/sin(elevation_.get());}
      /** Accessor to measured sky brightness temperature */
      vector<Temperature> getmeasuredSkyBrightness(){return v_measuredSkyBrightness_;}
      /** Accessor to fitted sky brightness temperatures */
      vector<Temperature> getfittedSkyBrightness(){return v_fittedSkyBrightness_;}
      /** Setter of fitted sky brightness temperatures */
      void setfittedSkyBrightness(vector<Temperature> a){v_fittedSkyBrightness_ = a;}
      /** Accessor to retrieved water vapor column */
      Length getretrievedWaterVaporColumn(){return retrievedWaterVaporColumn_;}
      /** Setter of retrieved water vapor column */
      void setretrievedWaterVaporColumn(Length a){retrievedWaterVaporColumn_ = a;}
      /** Accessor to sigma of the fit (in K) */
      Temperature getSigmaFit(){return sigma_fittedSkyBrightness_;}
      /** Setter of sigma of the fit (in K) */
      void setSigmaFit(Temperature a){sigma_fittedSkyBrightness_ = a;}
      
      
    protected:
      Angle elevation_;
      vector<Temperature> v_measuredSkyBrightness_;
      vector<Temperature> v_fittedSkyBrightness_;         // !< Fitted sky brightness temperatures over all WVR channels for each event
      Length  retrievedWaterVaporColumn_;           // !< Retrieved zenith water vapor column for each event  
      Temperature sigma_fittedSkyBrightness_;          // !< Sigma on the fitted sky brightness temperatures (average sigma over the WVR channels for each event). 

      
    };
}

#define ATM_WVRMEASUREMENT_H
#endif
