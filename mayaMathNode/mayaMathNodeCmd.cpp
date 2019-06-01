#include <string.h>
#include <maya/MIOStream.h>
#include <math.h>
#include <maya/MPxNode.h> 
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnPlugin.h>
#include <maya/MString.h> 
#include <maya/MTypeId.h> 
#include <maya/MPlug.h>
#include <maya/MVector.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
 

// written by dango(wangdonghao)

class mayaMathNode : public MPxNode
{
public:
 mayaMathNode();
    virtual ~mayaMathNode(); 
    virtual MStatus compute( const MPlug& plug, MDataBlock& data );
    static void* creator();
    static MStatus initialize();
public:
    static MObject input1;
	static MObject input2; 
    static MObject sineOut; 
	static MObject cosOut; 
	static MObject tanOut; 
	static MObject piOut; 
	static MObject modOut; 
	static MObject logOut; 
	static MObject expOut;
	static MObject powOut;
	static MObject floorOut;
	static MObject ceilOut;
    static MTypeId id;
};
MTypeId mayaMathNode::id( 0x80012 );
MObject mayaMathNode::input1; 
MObject mayaMathNode::input2; 
MObject mayaMathNode::sineOut; 
MObject mayaMathNode::cosOut; 
MObject mayaMathNode::tanOut; 
MObject mayaMathNode::piOut;
MObject mayaMathNode::modOut; 
MObject mayaMathNode::logOut; 
MObject mayaMathNode::expOut; 
MObject mayaMathNode::powOut;
MObject mayaMathNode::floorOut;
MObject mayaMathNode::ceilOut;
mayaMathNode::mayaMathNode() {}
mayaMathNode::~mayaMathNode() {}
MStatus mayaMathNode::compute( const MPlug& plug, MDataBlock& data )
{
    
    MStatus returnStatus;
 
  
        MDataHandle inputData = data.inputValue( input1, &returnStatus );
		MDataHandle inputData2 = data.inputValue( input2, &returnStatus );
        if( returnStatus != MS::kSuccess )
 cerr << "ERROR getting data" << endl;
        else
        {
			//float result = inputData.asFloat();
			if( plug == sineOut ){
			float result = sinf( inputData.asFloat() );
			MDataHandle sineOutHandle = data.outputValue( mayaMathNode::sineOut );
			sineOutHandle.set( result );
			data.setClean(plug);
			}
			else if( plug == cosOut ){
			float result = cosf(inputData.asFloat());
			MDataHandle cosOutHandle = data.outputValue( mayaMathNode::cosOut );
			cosOutHandle.set( result );
			data.setClean(plug);
			}
			else if( plug == tanOut ){
			float result = tanf(inputData.asFloat());
			MDataHandle tanOutHandle = data.outputValue( mayaMathNode::tanOut );
			tanOutHandle.set( result );
			data.setClean(plug);
			}
			else if( plug == piOut ){
			float result =  inputData.asFloat() * M_PI;;
			MDataHandle piOutHandle = data.outputValue( mayaMathNode::piOut );
			piOutHandle.set( result );
			data.setClean(plug);
			}
            else if( plug == modOut ){
			float result = fmod(inputData.asFloat(), inputData2.asFloat());
			MDataHandle modOutHandle = data.outputValue( mayaMathNode::modOut );
			modOutHandle.set( result );
			data.setClean(plug);
			}
			else if( plug == logOut ){
			float result = logf(inputData.asFloat());
			MDataHandle logOutHandle = data.outputValue( mayaMathNode::logOut );
			logOutHandle.set( result );
			data.setClean(plug);
			}
			else if( plug == expOut ){
			float result = expf(inputData.asFloat());
			MDataHandle expOutHandle = data.outputValue( mayaMathNode::expOut );
			expOutHandle.set( result );
			data.setClean(plug);
			}
			else if( plug == powOut ){
			float result = powf(inputData.asFloat(), inputData2.asFloat());
			MDataHandle powOutHandle = data.outputValue( mayaMathNode::powOut );
			powOutHandle.set( result );
			data.setClean(plug);
			}
			else if( plug == floorOut ){
			float result = floorf(inputData.asFloat());
			MDataHandle floorOutHandle = data.outputValue( mayaMathNode::floorOut );
			floorOutHandle.set( result );
			data.setClean(plug);
			}
			else if( plug == ceilOut ){
			float result = floorf(inputData.asFloat());
			MDataHandle ceilOutHandle = data.outputValue( mayaMathNode::ceilOut );
			ceilOutHandle.set( result );
			data.setClean(plug);
			}
        } 
    return MS::kSuccess;
}
void* mayaMathNode::creator()
{
    return new mayaMathNode();
}
MStatus mayaMathNode::initialize()
{
    MFnNumericAttribute nAttr;
    MStatus stat;
 input1 = nAttr.create( "input1", "in1", MFnNumericData::kFloat, 0.0 );
 nAttr.setStorable(true);
 input2 = nAttr.create( "input2", "in2", MFnNumericData::kFloat, 0.0 );
 nAttr.setStorable(true);
 sineOut = nAttr.create( "sineOut", "sineOut", MFnNumericData::kFloat, 0.0 );
 nAttr.setWritable(false);
 nAttr.setStorable(false);
 cosOut = nAttr.create( "cosOut", "cosOut", MFnNumericData::kFloat, 0.0 );
 nAttr.setWritable(false);
 nAttr.setStorable(false);
 tanOut = nAttr.create( "tanOut", "tanOut", MFnNumericData::kFloat, 0.0 );
 nAttr.setWritable(false);
 nAttr.setStorable(false);
 piOut = nAttr.create( "piOut", "piOut", MFnNumericData::kFloat, 0.0 );
 nAttr.setWritable(false);
 nAttr.setStorable(false);
 modOut = nAttr.create( "modOut", "modOut", MFnNumericData::kFloat, 0.0 );
 nAttr.setWritable(false);
 nAttr.setStorable(false);
 logOut = nAttr.create( "logOut", "logOut", MFnNumericData::kFloat, 0.0 );
 nAttr.setWritable(false);
 nAttr.setStorable(false);
 expOut = nAttr.create( "expOut", "expOut", MFnNumericData::kFloat, 0.0 );
 nAttr.setWritable(false);
 nAttr.setStorable(false);
 powOut = nAttr.create( "powOut", "powOut", MFnNumericData::kFloat, 0.0 );
 nAttr.setWritable(false);
 nAttr.setStorable(false);
 floorOut = nAttr.create( "floorOut", "floorOut", MFnNumericData::kFloat, 0.0 );
 nAttr.setWritable(false);
 nAttr.setStorable(false);
 ceilOut = nAttr.create( "ceilOut", "ceilOut", MFnNumericData::kFloat, 0.0 );
 nAttr.setWritable(false);
 nAttr.setStorable(false);

 stat = addAttribute( input1 );
        if (!stat) { stat.perror("addAttribute"); return stat;}
stat = addAttribute( input2 );
if (!stat) { stat.perror("addAttribute"); return stat;}

 stat = addAttribute( sineOut );
        if (!stat) { stat.perror("addAttribute"); return stat;}
 stat = attributeAffects( input1, sineOut );
        if (!stat) { stat.perror("attributeAffects"); return stat;}

stat = addAttribute( cosOut );
if (!stat) { stat.perror("addAttribute"); return stat;}
stat = attributeAffects( input1, cosOut );
if (!stat) { stat.perror("attributeAffects"); return stat;}

stat = addAttribute( tanOut );
if (!stat) { stat.perror("addAttribute"); return stat;}
stat = attributeAffects( input1, tanOut );
if (!stat) { stat.perror("attributeAffects"); return stat;}

stat = addAttribute( piOut );
if (!stat) { stat.perror("addAttribute"); return stat;}
stat = attributeAffects( input1, piOut );
if (!stat) { stat.perror("attributeAffects"); return stat;}

 stat = addAttribute( modOut );
		if (!stat) { stat.perror("addAttribute"); return stat;}
 stat = attributeAffects( input1, modOut );
        if (!stat) { stat.perror("attributeAffects"); return stat;}

 stat = addAttribute( logOut );
		if (!stat) { stat.perror("addAttribute"); return stat;}
 stat = attributeAffects( input1, logOut );
        if (!stat) { stat.perror("attributeAffects"); return stat;}
 stat = addAttribute( expOut );
		if (!stat) { stat.perror("addAttribute"); return stat;}
 stat = attributeAffects( input1, expOut );
        if (!stat) { stat.perror("attributeAffects"); return stat;}
 stat = addAttribute( powOut );
		if (!stat) { stat.perror("addAttribute"); return stat;}
 stat = attributeAffects( input1, powOut );
        if (!stat) { stat.perror("attributeAffects"); return stat;}
 stat = addAttribute( floorOut );
		if (!stat) { stat.perror("addAttribute"); return stat;}
 stat = attributeAffects( input1, floorOut );
        if (!stat) { stat.perror("attributeAffects"); return stat;}
 stat = addAttribute( ceilOut );
		if (!stat) { stat.perror("addAttribute"); return stat;}
 stat = attributeAffects( input1, ceilOut );
        if (!stat) { stat.perror("attributeAffects"); return stat;}

    return MS::kSuccess;
}
MStatus initializePlugin( MObject obj )
{ 
    MStatus status;
    MFnPlugin plugin( obj, PLUGIN_COMPANY, "1.0", "Any");
 status = plugin.registerNode( "mayaMathNode", mayaMathNode::id, mayaMathNode::creator,
 mayaMathNode::initialize );
    if (!status) {
 status.perror("registerNode");
        return status;
    }
    return status;
}
MStatus uninitializePlugin( MObject obj)
{
    MStatus status;
    MFnPlugin plugin( obj );
 status = plugin.deregisterNode( mayaMathNode::id );
    if (!status) {
 status.perror("deregisterNode");
        return status;
    }
    return status;
}