Module uim.codec.format.WILL_2_0_0_pb2
======================================
Generated protocol buffer code.

Classes
-------

`ParticlesPaint(**kwargs)`
:   Abstract base class for protocol messages.
    
    Protocol message classes are almost always generated by the protocol
    compiler.  These generated types subclass Message and implement the methods
    shown below.

    ### Ancestors (in MRO)

    * google.protobuf.message.Message

    ### Class variables

    `COMPOSITEOPERATION_FIELD_NUMBER`
    :

    `DESCRIPTOR`
    :

    `FILLHEIGHT_FIELD_NUMBER`
    :

    `FILLWIDTH_FIELD_NUMBER`
    :

    `FILL_FIELD_NUMBER`
    :

    `ID_FIELD_NUMBER`
    :

    `NONE`
    :

    `RANDOM`
    :

    `RANDOMIZEFILL_FIELD_NUMBER`
    :

    `ROTATION_FIELD_NUMBER`
    :

    `Rotation`
    :

    `SCATTERING_FIELD_NUMBER`
    :

    `SHAPE_FIELD_NUMBER`
    :

    `SPACING_FIELD_NUMBER`
    :

    `TRAJECTORY`
    :

    ### Static methods

    `FromString(s)`
    :

    `RegisterExtension(extension_handle)`
    :

    ### Instance variables

    `compositeOperation`
    :   Getter for compositeOperation.

    `fill`
    :   Getter for fill.

    `fillHeight`
    :   Getter for fillHeight.

    `fillWidth`
    :   Getter for fillWidth.

    `id`
    :   Getter for id.

    `randomizeFill`
    :   Getter for randomizeFill.

    `rotation`
    :   Getter for rotation.

    `scattering`
    :   Getter for scattering.

    `shape`
    :   Getter for shape.

    `spacing`
    :   Getter for spacing.

    ### Methods

    `ByteSize(self)`
    :

    `Clear(self)`
    :

    `ClearField(self, field_name)`
    :

    `DiscardUnknownFields(self)`
    :

    `FindInitializationErrors(self)`
    :   Finds required fields which are not initialized.
        
        Returns:
          A list of strings.  Each string is a path to an uninitialized field from
          the top-level message, e.g. "foo.bar[5].baz".

    `HasField(self, field_name)`
    :

    `IsInitialized(self, errors=None)`
    :   Checks if all required fields of a message are set.
        
        Args:
          errors:  A list which, if provided, will be populated with the field
                   paths of all missing required fields.
        
        Returns:
          True iff the specified message has all required fields set.

    `ListFields(self)`
    :

    `MergeFrom(self, msg)`
    :

    `MergeFromString(self, serialized)`
    :

    `SerializePartialToString(self, **kwargs)`
    :

    `SerializeToString(self, **kwargs)`
    :

    `SetInParent(self)`
    :   Sets the _cached_byte_size_dirty bit to true,
        and propagates this to our listener iff this was a state change.

    `UnknownFields(self)`
    :

    `WhichOneof(self, oneof_name)`
    :   Returns the name of the currently set field inside a oneof, or None.

`Path(**kwargs)`
:   Abstract base class for protocol messages.
    
    Protocol message classes are almost always generated by the protocol
    compiler.  These generated types subclass Message and implement the methods
    shown below.

    ### Ancestors (in MRO)

    * google.protobuf.message.Message

    ### Class variables

    `COMPOSITEOPERATION_FIELD_NUMBER`
    :

    `DATA_FIELD_NUMBER`
    :

    `DECIMALPRECISION_FIELD_NUMBER`
    :

    `DESCRIPTOR`
    :

    `ENDPARAMETER_FIELD_NUMBER`
    :

    `ID_FIELD_NUMBER`
    :

    `STARTPARAMETER_FIELD_NUMBER`
    :

    `STROKECOLOR_FIELD_NUMBER`
    :

    `STROKEPAINT_FIELD_NUMBER`
    :

    `STROKEPARTICLESRANDOMSEED_FIELD_NUMBER`
    :

    `STROKEWIDTH_FIELD_NUMBER`
    :

    ### Static methods

    `FromString(s)`
    :

    `RegisterExtension(extension_handle)`
    :

    ### Instance variables

    `compositeOperation`
    :   Getter for compositeOperation.

    `data`
    :   Getter for data.

    `decimalPrecision`
    :   Getter for decimalPrecision.

    `endParameter`
    :   Getter for endParameter.

    `id`
    :   Getter for id.

    `startParameter`
    :   Getter for startParameter.

    `strokeColor`
    :   Getter for strokeColor.

    `strokePaint`
    :   Getter for strokePaint.

    `strokeParticlesRandomSeed`
    :   Getter for strokeParticlesRandomSeed.

    `strokeWidth`
    :   Getter for strokeWidth.

    ### Methods

    `ByteSize(self)`
    :

    `Clear(self)`
    :

    `ClearField(self, field_name)`
    :

    `DiscardUnknownFields(self)`
    :

    `FindInitializationErrors(self)`
    :   Finds required fields which are not initialized.
        
        Returns:
          A list of strings.  Each string is a path to an uninitialized field from
          the top-level message, e.g. "foo.bar[5].baz".

    `HasField(self, field_name)`
    :

    `IsInitialized(self, errors=None)`
    :   Checks if all required fields of a message are set.
        
        Args:
          errors:  A list which, if provided, will be populated with the field
                   paths of all missing required fields.
        
        Returns:
          True iff the specified message has all required fields set.

    `ListFields(self)`
    :

    `MergeFrom(self, msg)`
    :

    `MergeFromString(self, serialized)`
    :

    `SerializePartialToString(self, **kwargs)`
    :

    `SerializeToString(self, **kwargs)`
    :

    `SetInParent(self)`
    :   Sets the _cached_byte_size_dirty bit to true,
        and propagates this to our listener iff this was a state change.

    `UnknownFields(self)`
    :

    `WhichOneof(self, oneof_name)`
    :   Returns the name of the currently set field inside a oneof, or None.