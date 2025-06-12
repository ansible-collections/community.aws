#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: medialive_channel
version_added: 10.1.0
short_description: Manage AWS MediaLive Anywhere Channels
description:
  - A module for creating, updating and deleting AWS MediaLive Channels.
  - This module includes basic functionality for managing channels, but does not include input validation
  - Requires boto3 >= 1.37.30
author:
  - "Sergey Papyan"
options:
  cdi_input_specification:
    description:
      - Specification of CDI inputs for this channel
    type: dict
    suboptions:
      resolution:
        description:
          - Maximum CDI input resolution
        type: str
        choices: ['SD', 'HD', 'FHD', 'UHD']
  channel_class:
    description:
      - The class for this channel. STANDARD for a channel with two pipelines or SINGLE_PIPELINE for a channel with one pipeline.
    type: str
    choices: ['STANDARD', 'SINGLE_PIPELINE']
  destinations:
    description:
      - A list of output destinations for this channel. Defines where and how the outputs of the MediaLive channel should be delivered.
    type: list
    elements: dict
    suboptions:
      id:
        description:
          - User-specified id. This is used in an output group or an output.
        type: str
      media_package_settings:
        description:
          - Destination settings for a MediaPackage output; one destination for both encoders.
        type: list
        elements: dict
        suboptions:
          channel_id:
            description:
              - ID of the channel in MediaPackage that is the destination for this output group. You do not need to specify the individual inputs in MediaPackage; MediaLive will handle the connection of the two MediaLive pipelines to the two MediaPackage inputs. The MediaPackage channel and MediaLive channel must be in the same region.
            type: str
          channel_group:
            description:
              - Name of the channel group in MediaPackageV2. Only use if you are sending CMAF Ingest output to a CMAF ingest endpoint on a MediaPackage channel that uses MediaPackage v2.
            type: str
          channel_name:
            description:
              - Name of the channel in MediaPackageV2. Only use if you are sending CMAF Ingest output to a CMAF ingest endpoint on a MediaPackage channel that uses MediaPackage v2.
            type: str
      multiplex_settings:
        description:
          - Destination settings for a Multiplex output; one destination for both encoders.
        type: dict
        suboptions:
          multiplex_id:
            description:
              - The ID of the Multiplex that the encoder is providing output to. You do not need to specify the individual inputs to the Multiplex; MediaLive will handle the connection of the two MediaLive pipelines to the two Multiplex instances. The Multiplex must be in the same region as the Channel.
            type: str
          program_name:
            description:
              - The program name of the Multiplex program that the encoder is providing output to.
            type: str
      settings:
        description:
          - Destination settings for a standard output; one destination for each redundant encoder.
        type: list
        elements: dict
        suboptions:
          password_param:
            description:
              - key used to extract the password from EC2 Parameter store
            type: str
          stream_name:
            description:
              - Stream name for RTMP destinations (URLs of type rtmp://)
            type: str
          url:
            description:
              - A URL specifying a destination
            type: str
          username:
            description:
              - username for destination
            type: str
      srt_settings:
        description:
          - SRT settings for an SRT output; one destination for each redundant encoder.
        type: list
        elements: dict
        suboptions:
          encryption_passphrase_secret_arn:
            description:
              - Arn used to extract the password from Secrets Manager
            type: str
          stream_id:
            description:
              - Stream id for SRT destinations (URLs of type srt://)
            type: str
          url:
            description:
              - A URL specifying a destination
            type: str
      logical_interface_names:
        description:
          - A list of logical interface names used for network isolation in MediaLive Anywhere deployments.

        type: list
        elements: str
  encoder_settings:
    description:
      - Encoder Settings
    type: dict
    suboptions:
      audio_descriptions:
        description:
          - Placeholder documentation for __listOfAudioDescription
        type: list
        elements: dict
        suboptions:
          audio_normalization_settings:
            description:
              - Advanced audio normalization settings.
            type: dict
            suboptions:
              algorithm:
                description:
                  - Audio normalization algorithm to use. itu17701 conforms to the CALM Act specification, itu17702 conforms to the EBU R-128 specification.
                type: str
                choices: ['ITU_1770_1', 'ITU_1770_2']
              algorithm_control:
                description:
                  - When set to correctAudio the output audio is corrected using the chosen algorithm. If set to measureOnly, the audio will be measured but not adjusted.
                type: str
                choices: ['CORRECT_AUDIO']
              target_lkfs:
                description:
                  - Target LKFS(loudness) to adjust volume to. If no value is entered, a default value will be used according to the chosen algorithm.
                  - The CALM Act (1770-1) recommends a target of -24 LKFS. The EBU R-128 specification (1770-2) recommends a target of -23 LKFS.
                type: float
          audio_selector_name:
            description:
              - The name of the AudioSelector used as the source for this AudioDescription.
            type: str
          audio_type:
            description:
              - Applies only if audioTypeControl is useConfigured. The values for audioType are defined in ISO-IEC 13818-1.
            type: str
            choices: ['CLEAN_EFFECTS', 'HEARING_IMPAIRED', 'UNDEFINED', 'VISUAL_IMPAIRED_COMMENTARY']
          audio_type_control:
            description:
              - Determines how audio type is determined. followInput - If the input contains an ISO 639 audioType, then that value is passed through to the output.
              - If the input contains no ISO 639 audioType, the value in Audio Type is included in the output.
              - useConfigured - The value in Audio Type is included in the output.
              - Note that this field and audioType are both ignored if inputType is broadcasterMixedAd.
            type: str
            choices: ['FOLLOW_INPUT', 'USE_CONFIGURED']
          audio_watermarking_settings:
            description:
              - Settings to configure one or more solutions that insert audio watermarks in the audio encode
            type: dict
            suboptions:
              nielsen_watermarks_settings:
                description:
                  - Settings to configure Nielsen Watermarks in the audio encode
                type: dict
                suboptions:
                  nielsen_cbet_settings:
                    description:
                      - Complete these fields only if you want to insert watermarks of type Nielsen CBET
                    type: dict
                    suboptions:
                      cbet_check_digit_string:
                        description:
                          - Enter the CBET check digits to use in the watermark.
                        type: str
                      cbet_stepaside:
                        description:
                          - Determines the method of CBET insertion mode when prior encoding is detected on the same layer.
                        type: str
                        choices: ['DISABLED', 'ENABLED']
                      csid:
                        description:
                          - Enter the CBET Source ID (CSID) to use in the watermark
                        type: str
              nielsen_distribution_type:
                description:
                  - Choose the distribution types that you want to assign to the watermarks - PROGRAM_CONTENT or FINAL_DISTRIBUTOR
                type: str
                choices: ['FINAL_DISTRIBUTOR', 'PROGRAM_CONTENT']
              nielsen_naes_ii_nw_settings:
                description:
                  - Complete these fields only if you want to insert watermarks of type Nielsen NAES II (N2) and Nielsen NAES VI (NW).
                type: dict
                suboptions:
                  check_digit_string:
                    description:
                      - Enter the check digit string for the watermark
                    type: str
                  sid:
                    description:
                      - Enter the Nielsen Source ID (SID) to include in the watermark
                    type: float
                  timezone:
                    description:
                      - Choose the timezone for the time stamps in the watermark. If not provided, the timestamps will be in Coordinated Universal Time (UTC)
                    type: str
                    choices:
                      - 'AMERICA_PUERTO_RICO'
                      - 'US_ALASKA'
                      - 'US_ARIZONA'
                      - 'US_CENTRAL'
                      - 'US_EASTERN'
                      - 'US_HAWAII'
                      - 'US_MOUNTAIN'
                      - 'US_PACIFIC'
                      - 'US_SAMOA'
                      - 'UTC'
          codec_settings:
            description:
              - Audio codec settings.
            type: dict
            suboptions:
              aac_settings:
                description:
                  - Aac Settings
                type: dict
                suboptions:
                  bitrate:
                    description:
                      - Average bitrate in bits/second. Valid values depend on rate control mode and profile.
                    type: float
                  coding_mode:
                    description:
                      - Mono, Stereo, or 5.1 channel layout. Valid values depend on rate control mode and profile.
                      - The adReceiverMix setting receives a stereo description plus control track and emits a mono AAC encode of the description track, with control data emitted in the PES header as per ETSI TS 101 154 Annex E.
                    type: str
                    choices:
                      - 'AD_RECEIVER_MIX'
                      - 'CODING_MODE_1_0'
                      - 'CODING_MODE_1_1'
                      - 'CODING_MODE_2_0'
                      - 'CODING_MODE_5_1'
                  input_type:
                    description:
                      - Set to "broadcasterMixedAd" when input contains pre-mixed main audio + AD (narration) as a stereo pair.
                      - The Audio Type field (audioType) will be set to 3, which signals to downstream systems that this stream contains "broadcaster mixed AD".
                      - Note that the input received by the encoder must contain pre-mixed audio; the encoder does not perform the mixing.
                      - The values in audioTypeControl and audioType (in AudioDescription) are ignored when set to broadcasterMixedAd.
                      - Leave set to "normal" when input does not contain pre-mixed audio + AD.
                    type: str
                    choices: ['BROADCASTER_MIXED_AD', 'NORMAL']
                  profile:
                    description:
                      - AAC Profile.
                    type: str
                    choices: ['HEV1', 'HEV2', 'LC']
                  rate_control_mode:
                    description:
                      - Rate Control Mode.
                    type: str
                    choices: ['CBR', 'VBR']
                  raw_format:
                    description:
                      - Sets LATM / LOAS AAC output for raw containers.
                    type: str
                    choices: ['LATM_LOAS', 'NONE']
                  sample_rate:
                    description:
                      - Sample rate in Hz. Valid values depend on rate control mode and profile.
                    type: float
                  spec:
                    description:
                      - Use MPEG-2 AAC audio instead of MPEG-4 AAC audio for raw or MPEG-2 Transport Stream containers.
                    type: str
                    choices: ['MPEG2', 'MPEG4']
                  vbr_quality:
                    description:
                      - VBR Quality Level - Only used if rateControlMode is VBR.
                    type: str
                    choices: ['HIGH', 'LOW', 'MEDIUM_HIGH', 'MEDIUM_LOW']
              ac3_settings:
                description:
                  - Ac3 Settings
                type: dict
                suboptions:
                  bitrate:
                    description:
                      - Average bitrate in bits/second. Valid bitrates depend on the coding mode.
                    type: float
                  bitstream_mode:
                    description:
                      - Specifies the bitstream mode (bsmod) for the emitted AC-3 stream. See ATSC A/52-2012 for background on these values.
                    type: str
                    choices:
                      - 'COMMENTARY'
                      - 'COMPLETE_MAIN'
                      - 'DIALOGUE'
                      - 'EMERGENCY'
                      - 'HEARING_IMPAIRED'
                      - 'MUSIC_AND_EFFECTS'
                      - 'VISUALLY_IMPAIRED'
                      - 'VOICE_OVER'
                  coding_mode:
                    description:
                      - Dolby Digital coding mode. Determines number of channels.
                    type: str
                    choices: ['CODING_MODE_1_0', 'CODING_MODE_1_1', 'CODING_MODE_2_0', 'CODING_MODE_3_2_LFE']
                  dialnorm:
                    description:
                      - Sets the dialnorm for the output. If excluded and input audio is Dolby Digital, dialnorm will be passed through.
                    type: float
                  drc_profile:
                    description:
                      - If set to filmStandard, adds dynamic range compression signaling to the output bitstream as defined in the Dolby Digital specification.
                    type: str
                    choices: ['FILM_STANDARD', 'NONE']
                  lfe_filter:
                    description:
                      - When set to enabled, applies a 120Hz lowpass filter to the LFE channel prior to encoding. Only valid in codingMode32Lfe mode.
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  metadata_control:
                    description:
                      - When set to "followInput", encoder metadata will be sourced from the DD, DD+, or DolbyE decoder that supplied this audio data. If audio was not supplied from one of these streams, then the static metadata settings will be used.
                    type: str
                    choices: ['FOLLOW_INPUT', 'USE_CONFIGURED']
                  attenuation_control:
                    description:
                      - Applies a 3 dB attenuation to the surround channels. Applies only when the coding mode parameter is CODING_MODE_3_2_LFE.
                    type: str
                    choices: ['ATTENUATE_3_DB', 'NONE']
              eac3_atmos_settings:
                description:
                  - Eac3 Atmos Settings
                type: dict
                suboptions:
                  bitrate:
                    description:
                      - Average bitrate in bits/second. Valid bitrates depend on the coding mode.
                    type: float
                  coding_mode:
                    description:
                      - Dolby Digital Plus with Dolby Atmos coding mode. Determines number of channels.
                    type: str
                    choices: ['CODING_MODE_5_1_4', 'CODING_MODE_7_1_4', 'CODING_MODE_9_1_6']
                  dialnorm:
                    description:
                      - Sets the dialnorm for the output. Default 23.
                    type: int
                  drc_line:
                    description:
                      - Sets the Dolby dynamic range compression profile.
                    type: str
                    choices:
                      - 'FILM_LIGHT'
                      - 'FILM_STANDARD'
                      - 'MUSIC_LIGHT'
                      - 'MUSIC_STANDARD'
                      - 'NONE'
                      - 'SPEECH'
                  drc_rf:
                    description:
                      - Sets the profile for heavy Dolby dynamic range compression, ensures that the instantaneous signal peaks do not exceed specified levels.
                    type: str
                    choices:
                      - 'FILM_LIGHT'
                      - 'FILM_STANDARD'
                      - 'MUSIC_LIGHT'
                      - 'MUSIC_STANDARD'
                      - 'NONE'
                      - 'SPEECH'
                  height_trim:
                    description:
                      - Height dimensional trim. Sets the maximum amount to attenuate the height channels when the downstream player isn't configured to handle Dolby Digital Plus with Dolby Atmos and must remix the channels.
                    type: float
                  surround_trim:
                    description:
                      - Surround dimensional trim. Sets the maximum amount to attenuate the surround channels when the downstream player isn't configured to handle Dolby Digital Plus with Dolby Atmos and must remix the channels.
                    type: float
              eac3_settings:
                description:
                  - Eac3 Settings
                type: dict
                suboptions:
                  attenuation_control:
                    description:
                      - When set to attenuate3Db, applies a 3 dB attenuation to the surround channels. Only used for 3/2 coding mode.
                    type: str
                    choices: ['ATTENUATE_3_DB', 'NONE']
                  bitrate:
                    description:
                      - Average bitrate in bits/second. Valid bitrates depend on the coding mode.
                    type: float
                  bitstream_mode:
                    description:
                      - Specifies the bitstream mode (bsmod) for the emitted E-AC-3 stream. See ATSC A/52-2012 (Annex E) for background on these values.
                    type: str
                    choices:
                      - 'COMMENTARY'
                      - 'COMPLETE_MAIN'
                      - 'EMERGENCY'
                      - 'HEARING_IMPAIRED'
                      - 'VISUALLY_IMPAIRED'
                  coding_mode:
                    description:
                      - Dolby Digital Plus coding mode. Determines number of channels.
                    type: str
                    choices: ['CODING_MODE_1_0', 'CODING_MODE_2_0', 'CODING_MODE_3_2']
                  dc_filter:
                    description:
                      - When set to enabled, activates a DC highpass filter for all input channels.
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  dialnorm:
                    description:
                      - Sets the dialnorm for the output. If blank and input audio is Dolby Digital Plus, dialnorm will be passed through.
                    type: float
                  drc_line:
                    description:
                      - Sets the Dolby dynamic range compression profile.
                    type: str
                    choices:
                      - 'FILM_LIGHT'
                      - 'FILM_STANDARD'
                      - 'MUSIC_LIGHT'
                      - 'MUSIC_STANDARD'
                      - 'NONE'
                      - 'SPEECH'
                  drc_rf:
                    description:
                      - Sets the profile for heavy Dolby dynamic range compression, ensures that the instantaneous signal peaks do not exceed specified levels.
                    type: str
                    choices:
                      - 'FILM_LIGHT'
                      - 'FILM_STANDARD'
                      - 'MUSIC_LIGHT'
                      - 'MUSIC_STANDARD'
                      - 'NONE'
                      - 'SPEECH'
                  lfe_control:
                    description:
                      - When encoding 3/2 audio, setting to lfe enables the LFE channel
                    type: str
                    choices: ['LFE', 'NO_LFE']
                  lfe_filter:
                    description:
                      - When set to enabled, applies a 120Hz lowpass filter to the LFE channel prior to encoding. Only valid with codingMode32 coding mode.
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  lo_ro_center_mix_level:
                    description:
                      - Left only/Right only center mix level. Only used for 3/2 coding mode.
                    type: float
                  lo_ro_surround_mix_level:
                    description:
                      - Left only/Right only surround mix level. Only used for 3/2 coding mode.
                    type: float
                  lt_rt_center_mix_level:
                    description:
                      - Left total/Right total center mix level. Only used for 3/2 coding mode.
                    type: float
                  lt_rt_surround_mix_level:
                    description:
                      - Left total/Right total surround mix level. Only used for 3/2 coding mode.
                    type: float
                  metadata_control:
                    description:
                      - When set to followInput, encoder metadata will be sourced from the DD, DD+, or DolbyE decoder that supplied this audio data. If audio was not supplied from one of these streams, then the static metadata settings will be used.
                    type: str
                    choices: ['FOLLOW_INPUT', 'USE_CONFIGURED']
                  passthrough_control:
                    description:
                      - When set to whenPossible, input DD+ audio will be passed through if it is present on the input. This detection is dynamic over the life of the transcode. Inputs that alternate between DD+ and non-DD+ content will have a consistent DD+ output as the system alternates between passthrough and encoding.
                    type: str
                    choices: ['NO_PASSTHROUGH', 'WHEN_POSSIBLE']
                  phase_control:
                    description:
                      - When set to shift90Degrees, applies a 90-degree phase shift to the surround channels. Only used for 3/2 coding mode.
                    type: str
                    choices: ['NO_SHIFT', 'SHIFT_90_DEGREES']
                  stereo_downmix:
                    description:
                      - Stereo downmix preference. Only used for 3/2 coding mode.
                    type: str
                    choices: ['DPL2', 'LO_RO', 'LT_RT', 'NOT_INDICATED']
                  surround_ex_mode:
                    description:
                      - When encoding 3/2 audio, sets whether an extra center back surround channel is matrix encoded into the left and right surround channels.
                    type: str
                    choices: ['DISABLED', 'ENABLED', 'NOT_INDICATED']
                  surround_mode:
                    description:
                      - When encoding 2/0 audio, sets whether Dolby Surround is matrix encoded into the two channels.
                    type: str
                    choices: ['DISABLED', 'ENABLED', 'NOT_INDICATED']
              mp2_settings:
                description:
                  - Mp2 Settings
                type: dict
                suboptions:
                  bitrate:
                    description:
                      - Average bitrate in bits/second.
                    type: float
                  coding_mode:
                    description:
                      - The MPEG2 Audio coding mode. Valid values are codingMode10 (for mono) or codingMode20 (for stereo).
                    type: str
                    choices: ['CODING_MODE_1_0', 'CODING_MODE_2_0']
                  sample_rate:
                    description:
                      - Sample rate in Hz.
                    type: float
              pass_through_settings:
                description:
                  - Pass Through Settings
                type: dict
              wav_settings:
                description:
                  - Wav Settings
                type: dict
                suboptions:
                  bit_depth:
                    description:
                      - Bits per sample.
                    type: float
                  coding_mode:
                    description:
                      - The audio coding mode for the WAV audio. The mode determines the number of channels in the audio.
                    type: str
                    choices: ['CODING_MODE_1_0', 'CODING_MODE_2_0', 'CODING_MODE_4_0', 'CODING_MODE_8_0']
                  sample_rate:
                    description:
                      - Sample rate in Hz.
                    type: float
          language_code:
            description:
              - RFC 5646 language code representing the language of the audio output track. Only used if languageControlMode is useConfigured, or there is no ISO 639 language code specified in the input.
            type: str
          language_code_control:
            description:
              - Choosing followInput will cause the ISO 639 language code of the output to follow the ISO 639 language code of the input. The languageCode will be used when useConfigured is set, or when followInput is selected but there is no ISO 639 language code specified by the input.
            type: str
            choices: ['FOLLOW_INPUT', 'USE_CONFIGURED']
          name:
            description:
              - The name of this AudioDescription. Outputs will use this name to uniquely identify this AudioDescription. Description names should be unique within this Live Event.
            type: str
          remix_settings:
            description:
              - Settings that control how input audio channels are remixed into the output audio channels.
            type: dict
            suboptions:
              channel_mappings:
                description:
                  - Mapping of input channels to output channels, with appropriate gain adjustments.
                type: list
                elements: dict
                suboptions:
                  input_channel_levels:
                    description:
                      - Indices and gain values for each input channel that should be remixed into this output channel.
                    type: list
                    elements: dict
                    suboptions:
                      gain:
                        description:
                          - Remixing value. Units are in dB and acceptable values are within the range from -60 (mute) and 6 dB.
                        type: int
                      input_channel:
                        description:
                          - The index of the input channel used as a source.
                        type: int
                  output_channel:
                    description:
                      - The index of the output channel being produced.
                    type: int
              channels_in:
                description:
                  - Number of input channels to be used.
                type: int
              channels_out:
                description:
                  - Number of output channels to be produced. Valid values are 1, 2, 4, 6, 8
                type: int
          stream_name:
            description:
              - Used for MS Smooth and Apple HLS outputs. Indicates the name displayed by the player (eg. English, or Director Commentary).
            type: str
          audio_dash_roles:
            description:
              - Identifies the DASH roles to assign to this audio output. Applies only when the audio output is configured for DVB DASH accessibility signaling.
            type: list
            elements: str
            choices:
              - 'ALTERNATE'
              - 'COMMENTARY'
              - 'DESCRIPTION'
              - 'DUB'
              - 'EMERGENCY'
              - 'ENHANCED-AUDIO-INTELLIGIBILITY'
              - 'KARAOKE'
              - 'MAIN'
              - 'SUPPLEMENTARY'
          dvb_dash_accessibility:
            description:
              - Identifies DVB DASH accessibility signaling in this audio output. Used in Microsoft Smooth Streaming outputs to signal accessibility information to packagers.
            type: str
            choices:
              - 'DVBDASH_1_VISUALLY_IMPAIRED'
              - 'DVBDASH_2_HARD_OF_HEARING'
              - 'DVBDASH_3_SUPPLEMENTAL_COMMENTARY'
              - 'DVBDASH_4_DIRECTORS_COMMENTARY'
              - 'DVBDASH_5_EDUCATIONAL_NOTES'
              - 'DVBDASH_6_MAIN_PROGRAM'
              - 'DVBDASH_7_CLEAN_FEED'
      avail_blanking:
        description:
          - Settings for ad avail blanking.
        type: dict
        suboptions:
          avail_blanking_image:
            description:
              - Blanking image to be used. Leave empty for solid black. Only bmp and png images are supported.
            type: dict
            suboptions:
              password_param:
                description:
                  - key used to extract the password from EC2 Parameter store
                type: str
              uri:
                description:
                  - Uniform Resource Identifier - This should be a path to a file accessible to the Live system (eg. a http:// URI) depending on the output type. For example, a RTMP destination should have a uri simliar to "rtmp://fmsserver/live".
                type: str
              username:
                description:
                  - Documentation update needed
                type: str
          state:
            description:
              - When set to enabled, causes video, audio and captions to be blanked when insertion metadata is added.
            type: str
            choices: ['DISABLED', 'ENABLED']
      avail_configuration:
        description:
          - Event-wide configuration settings for ad avail insertion.
        type: dict
        suboptions:
          avail_settings:
            description:
              - Controls how SCTE-35 messages create cues. Splice Insert mode treats all segmentation signals traditionally. With Time Signal APOS mode only Time Signal Placement Opportunity and Break messages create segment breaks. With ESAM mode, signals are forwarded to an ESAM server for possible update.
            type: dict
            suboptions:
              esam:
                description:
                  - Esam
                type: dict
                suboptions:
                  acquisition_point_id:
                    description:
                      - Sent as acquisitionPointIdentity to identify the MediaLive channel to the POIS.
                    type: str
                  ad_avail_offset:
                    description:
                      - When specified, this offset (in milliseconds) is added to the input Ad Avail PTS time. This only applies to embedded SCTE 104/35 messages and does not apply to OOB messages.
                    type: int
                  password_param:
                    description:
                      - Documentation update needed
                    type: str
                  pois_endpoint:
                    description:
                      - The URL of the signal conditioner endpoint on the Placement Opportunity Information System (POIS). MediaLive sends SignalProcessingEvents here when SCTE-35 messages are read.
                    type: str
                  username:
                    description:
                      - Documentation update needed
                    type: str
                  zone_identity:
                    description:
                      - Optional data sent as zoneIdentity to identify the MediaLive channel to the POIS.
                    type: str
              scte35_splice_insert:
                description:
                  - Typical configuration that applies breaks on splice inserts in addition to time signal placement opportunities, breaks, and advertisements.
                type: dict
                suboptions:
                  ad_avail_offset:
                    description:
                      - When specified, this offset (in milliseconds) is added to the input Ad Avail PTS time. This only applies to embedded SCTE 104/35 messages and does not apply to OOB messages.
                    type: int
                  no_regional_blackout_flag:
                    description:
                      - When set to ignore, Segment Descriptors with noRegionalBlackoutFlag set to 0 will no longer trigger blackouts or Ad Avail slates
                    type: str
                    choices: ['FOLLOW', 'IGNORE']
                  web_delivery_allowed_flag:
                    description:
                      - When set to ignore, Segment Descriptors with webDeliveryAllowedFlag set to 0 will no longer trigger blackouts or Ad Avail slates
                    type: str
                    choices: ['FOLLOW', 'IGNORE']
              scte35_time_signal_apos:
                description:
                  - Atypical configuration that applies segment breaks only on SCTE-35 time signal placement opportunities and breaks.
                type: dict
                suboptions:
                  ad_avail_offset:
                    description:
                      - When specified, this offset (in milliseconds) is added to the input Ad Avail PTS time. This only applies to embedded SCTE 104/35 messages and does not apply to OOB messages.
                    type: int
                  no_regional_blackout_flag:
                    description:
                      - When set to ignore, Segment Descriptors with noRegionalBlackoutFlag set to 0 will no longer trigger blackouts or Ad Avail slates
                    type: str
                    choices: ['FOLLOW', 'IGNORE']
                  web_delivery_allowed_flag:
                    description:
                      - When set to ignore, Segment Descriptors with webDeliveryAllowedFlag set to 0 will no longer trigger blackouts or Ad Avail slates
                    type: str
                    choices: ['FOLLOW', 'IGNORE']
          scte35_segmentation_scope:
            description:
              - Configures whether SCTE 35 passthrough triggers segment breaks in all output groups that use segmented outputs. Insertion of a SCTE 35 message typically results in a segment break, in addition to the regular cadence of breaks. The segment breaks appear in video outputs, audio outputs, and captions outputs (if any).
              - ALL_OUTPUT_GROUPS - Default. Insert the segment break in in all output groups that have segmented outputs. This is the legacy behavior.
              - SCTE35_ENABLED_OUTPUT_GROUPS - Insert the segment break only in output groups that have SCTE 35 passthrough enabled. This is the recommended value, because it reduces unnecessary segment breaks.
            type: str
            choices: ['ALL_OUTPUT_GROUPS', 'SCTE35_ENABLED_OUTPUT_GROUPS']
      blackout_slate:
        description:
          - Settings for blackout slate.
        type: dict
        suboptions:
          blackout_slate_image:
            description:
              - Blackout slate image to be used. Leave empty for solid black. Only bmp and png images are supported.
            type: dict
            suboptions:
              password_param:
                description:
                  - key used to extract the password from EC2 Parameter store
                type: str
              uri:
                description:
                  - Uniform Resource Identifier - This should be a path to a file accessible to the Live system (eg. a http:// URI) depending on the output type. For example, a RTMP destination should have a uri simliar to "rtmp://fmsserver/live".
                type: str
              username:
                description:
                  - Documentation update needed
                type: str
          network_end_blackout:
            description:
              - Setting to enabled causes the encoder to blackout the video, audio, and captions, and raise the "Network Blackout Image" slate when an SCTE104/35 Network End Segmentation Descriptor is encountered. The blackout will be lifted when the Network Start Segmentation Descriptor is encountered. The Network End and Network Start descriptors must contain a network ID that matches the value entered in "Network ID".
            type: str
            choices: ['DISABLED', 'ENABLED']
          network_end_blackout_image:
            description:
              - Path to local file to use as Network End Blackout image. Image will be scaled to fill the entire output raster.
            type: dict
            suboptions:
              password_param:
                description:
                  - key used to extract the password from EC2 Parameter store
                type: str
              uri:
                description:
                  - Uniform Resource Identifier - This should be a path to a file accessible to the Live system (eg. a http:// URI) depending on the output type. For example, a RTMP destination should have a uri simliar to "rtmp://fmsserver/live".
                type: str
              username:
                description:
                  - Documentation update needed
                type: str
          network_id:
            description:
              - Provides Network ID that matches EIDR ID format (e.g., "10.XXXX/XXXX-XXXX-XXXX-XXXX-XXXX-C").
            type: str
          state:
            description:
              - When set to enabled, causes video, audio and captions to be blanked when indicated by program metadata.
            type: str
            choices: ['DISABLED', 'ENABLED']
      caption_descriptions:
        description:
          - Settings for caption decriptions
        type: list
        elements: dict
        suboptions:
          accessibility:
            description:
              - Indicates whether the caption track implements accessibility features such as written descriptions of spoken dialog, music, and sounds. This signaling is added to HLS output group and MediaPackage output group.
            type: str
            choices: ['DOES_NOT_IMPLEMENT_ACCESSIBILITY_FEATURES', 'IMPLEMENTS_ACCESSIBILITY_FEATURES']
          caption_selector_name:
            description:
              - Specifies which input caption selector to use as a caption source when generating output captions. This field should match a captionSelector name.
            type: str
          destination_settings:
            description:
              - Additional settings for captions destination that depend on the destination type.
            type: dict
            suboptions:
              arib_destination_settings:
                description:
                  - Arib Destination Settings
                type: dict
              burn_in_destination_settings:
                description:
                  - Burn In Destination Settings
                type: dict
                suboptions:
                  alignment:
                    description:
                      - If no explicit xPosition or yPosition is provided, setting alignment to centered will place the captions at the bottom center of the output. Similarly, setting a left alignment will align captions to the bottom left of the output. If x and y positions are given in conjunction with the alignment parameter, the font will be justified (either left or centered) relative to those coordinates. Selecting "smart" justification will left-justify live subtitles and center-justify pre-recorded subtitles. All burn-in and DVB-Sub font settings must match.
                    type: str
                    choices: ['CENTERED', 'LEFT', 'SMART']
                  background_color:
                    description:
                      - Specifies the color of the rectangle behind the captions. All burn-in and DVB-Sub font settings must match.
                    type: str
                    choices: ['BLACK', 'NONE', 'WHITE']
                  background_opacity:
                    description:
                      - Specifies the opacity of the background rectangle. 255 is opaque; 0 is transparent. Leaving this parameter out is equivalent to setting it to 0 (transparent). All burn-in and DVB-Sub font settings must match.
                    type: int
                  font:
                    description:
                      - External font file used for caption burn-in. File extension must be 'ttf' or 'tte'. Although the user can select output fonts for many different types of input captions, embedded, STL and teletext sources use a strict grid system. Using external fonts with these caption sources could cause unexpected display of proportional fonts. All burn-in and DVB-Sub font settings must match.
                    type: dict
                    suboptions:
                      password_param:
                        description:
                          - key used to extract the password from EC2 Parameter store
                        type: str
                      uri:
                        description:
                          - Uniform Resource Identifier - This should be a path to a file accessible to the Live system (eg. a http:// URI) depending on the output type. For example, a RTMP destination should have a uri simliar to "rtmp://fmsserver/live".
                        type: str
                      username:
                        description:
                          - Documentation update needed
                        type: str
                  font_color:
                    description:
                      - Specifies the color of the burned-in captions. This option is not valid for source captions that are STL, 608/embedded or teletext. These source settings are already pre-defined by the caption stream. All burn-in and DVB-Sub font settings must match.
                    type: str
                    choices:
                      - 'BLACK'
                      - 'BLUE'
                      - 'GREEN'
                      - 'RED'
                      - 'WHITE'
                      - 'YELLOW'
                  font_opacity:
                    description:
                      - TODO
                    type: int
                  font_resolution:
                    description:
                      - TODO
                    type: int
                  font_size:
                    description:
                      - TODO
                    type: str
              
                  outline_color:
                    description:
                      - TODO
                    type: str
                    choices:
                      - 'BLACK'
                      - 'BLUE'
                      - 'GREEN'
                      - 'RED'
                      - 'WHITE'
                      - 'YELLOW'
                  outline_size:
                    description:
                      - TODO
                    type: int
                  shadow_color:
                    description:
                      - TODO
                    type: str
                    choices: ['BLACK', 'NONE', 'WHITE']
                  shadow_opacity:
                    description:
                      - TODO
                    type: int
                  shadow_x_offset:
                    description:
                      - TODO
                    type: int
                  shadow_y_offset:
                    description:
                      - TODO
                    type: int
                  teletext_grid_control:
                    description:
                      - TODO
                    type: str
                    choices: ['FIXED', 'SCALED']
                  x_position:
                    description:
                      - TODO
                    type: int
                  y_position:
                    description:
                      - TODO
                    type: int
              dvb_sub_destination_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  alignment:
                    description:
                      - TODO
                    type: str
                    choices: ['CENTERED', 'LEFT', 'SMART']
                  background_color:
                    description:
                      - TODO
                    type: str
                    choices: ['BLACK', 'NONE', 'WHITE']
                  background_opacity:
                    description:
                      - TODO
                    type: int
                  font:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      password_param:
                        description:
                          - TODO
                        type: str
                      uri:
                        description:
                          - TODO
                        type: str
                      username:
                        description:
                          - TODO
                        type: str
                  font_color:
                    description:
                      - TODO
                    type: str
                    choices:
                      - 'BLACK'
                      - 'BLUE'
                      - 'GREEN'
                      - 'RED'
                      - 'WHITE'
                      - 'YELLOW'
                  font_opacity:
                    description:
                      - TODO
                    type: int
                  font_resolution:
                    description:
                      - TODO
                    type: int
                  font_size:
                    description:
                      - TODO
                    type: str
              
                  outline_color:
                    description:
                      - TODO
                    type: str
                    choices:
                      - 'BLACK'
                      - 'BLUE'
                      - 'GREEN'
                      - 'RED'
                      - 'WHITE'
                      - 'YELLOW'
                  outline_size:
                    description:
                      - TODO
                    type: int
                  shadow_color:
                    description:
                      - TODO
                    type: str
                    choices: ['BLACK', 'NONE', 'WHITE']
                  shadow_opacity:
                    description:
                      - TODO
                    type: int
                  shadow_x_offset:
                    description:
                      - TODO
                    type: int
                  shadow_y_offset:
                    description:
                      - TODO
                    type: int
                  teletext_grid_control:
                    description:
                      - TODO
                    type: str
                    choices: ['FIXED', 'SCALED']
                  x_position:
                    description:
                      - TODO
                    type: int
                  y_position:
                    description:
                      - TODO
                    type: int
              ebu_tt_d_destination_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  copyright_holder:
                    description:
                      - TODO
                    type: str
                  fill_line_gap:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  font_family:
                    description:
                      - TODO
                    type: str
                  style_control:
                    description:
                      - TODO
                    type: str
                    choices: ['EXCLUDE', 'INCLUDE']
                  default_font_size:
                    description:
                      - TODO
                    type: int
                  default_line_height:
                    description:
                      - TODO
                    type: int
              embedded_destination_settings:
                description:
                  - TODO
                type: dict
              embedded_plus_scte20_destination_settings:
                description:
                  - TODO
                type: dict
              rtmp_caption_info_destination_settings:
                description:
                  - TODO
                type: dict
              scte20_plus_embedded_destination_settings:
                description:
                  - TODO
                type: dict
              scte27_destination_settings:
                description:
                  - TODO
                type: dict
              smpte_tt_destination_settings:
                description:
                  - TODO
                type: dict
              teletext_destination_settings:
                description:
                  - TODO
                type: dict
              ttml_destination_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  style_control:
                    description:
                      - TODO
                    type: str
                    choices: ['PASSTHROUGH', 'USE_CONFIGURED']
              webvtt_destination_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  style_control:
                    description:
                      - TODO
                    type: str
                    choices: ['NO_STYLE_DATA', 'PASSTHROUGH']
          language_code:
            description:
              - TODO
            type: str
          language_description:
            description:
              - TODO
            type: str
          name:
            description:
              - TODO
            type: str
          caption_dash_roles:
            description:
              - TODO
            type: list
            elements: str
            choices:
              - 'ALTERNATE'
              - 'CAPTION'
              - 'COMMENTARY'
              - 'DESCRIPTION'
              - 'DUB'
              - 'EASYREADER'
              - 'EMERGENCY'
              - 'FORCED-SUBTITLE'
              - 'KARAOKE'
              - 'MAIN'
              - 'METADATA'
              - 'SUBTITLE'
              - 'SUPPLEMENTARY'
          dvb_dash_accessibility:
            description:
              - TODO
            type: str
            choices:
              - 'DVBDASH_1_VISUALLY_IMPAIRED'
              - 'DVBDASH_2_HARD_OF_HEARING'
              - 'DVBDASH_3_SUPPLEMENTAL_COMMENTARY'
              - 'DVBDASH_4_DIRECTORS_COMMENTARY'
              - 'DVBDASH_5_EDUCATIONAL_NOTES'
              - 'DVBDASH_6_MAIN_PROGRAM'
              - 'DVBDASH_7_CLEAN_FEED'
      feature_activations:
        description:
          - Feature Activations
        type: dict
        suboptions:
          input_prepare_schedule_actions:
            description:
              - Enables the Input Prepare feature. You can create Input Prepare actions in the schedule only if this feature is enabled. If you disable the feature on an existing schedule, make sure that you first delete all input prepare actions from the schedule.
            type: str
            choices: ['DISABLED', 'ENABLED']
          output_static_image_overlay_schedule_actions:
            description:
              - Enables the output static image overlay feature. Enabling this feature allows you to send channel schedule updates to display/clear/modify image overlays on an output-by-output bases.
            type: str
            choices: ['DISABLED', 'ENABLED']
      global_configuration:
        description:
          - Configuration settings that apply to the event as a whole.
        type: dict
        suboptions:
          initial_audio_gain:
            description:
              - Value to set the initial audio gain for the Live Event.
            type: int
          input_end_action:
            description:
              - Indicates the action to take when the current input completes (e.g. end-of-file). When switchAndLoopInputs is configured the encoder will restart at the beginning of the first input. When "none" is configured the encoder will transcode either black, a solid color, or a user specified slate images per the "Input Loss Behavior" configuration until the next input switch occurs (which is controlled through the Channel Schedule API).
            type: str
            choices: ['NONE', 'SWITCH_AND_LOOP_INPUTS']
          input_loss_behavior:
            description:
              - Settings for system actions when input is lost.
            type: dict
            suboptions:
              black_frame_msec:
                description:
                  - Documentation update needed
                type: int
              input_loss_image_color:
                description:
                  - When input loss image type is "color" this field specifies the color to use. Value - 6 hex characters representing the values of RGB.
                type: str
              input_loss_image_slate:
                description:
                  - When input loss image type is "slate" these fields specify the parameters for accessing the slate.
                type: dict
                suboptions:
                  password_param:
                    description:
                      - key used to extract the password from EC2 Parameter store
                    type: str
                  uri:
                    description:
                      - Uniform Resource Identifier - This should be a path to a file accessible to the Live system (eg. a http:// URI) depending on the output type. For example, a RTMP destination should have a uri simliar to "rtmp://fmsserver/live".
                    type: str
                  username:
                    description:
                      - Documentation update needed
                    type: str
              input_loss_image_type:
                description:
                  - Indicates whether to substitute a solid color or a slate into the output after input loss exceeds blackFrameMsec.
                type: str
                choices: ['COLOR', 'SLATE']
              repeat_frame_msec:
                description:
                  - Documentation update needed
                type: int
          output_locking_mode:
            description:
              - Indicates how MediaLive pipelines are synchronized. PIPELINE_LOCKING - MediaLive will attempt to synchronize the output of each pipeline to the other. EPOCH_LOCKING - MediaLive will attempt to synchronize the output of each pipeline to the Unix epoch. DISABLED - MediaLive will not attempt to synchronize the output of pipelines. We advise against disabling output locking because it has negative side effects in most workflows. For more information, see the section about output locking (pipeline locking) in the Medialive user guide.
            type: str
            choices: ['EPOCH_LOCKING', 'PIPELINE_LOCKING', 'DISABLED']
          output_timing_source:
            description:
              - Indicates whether the rate of frames emitted by the Live encoder should be paced by its system clock (which optionally may be locked to another source via NTP) or should be locked to the clock of the source that is providing the input stream.
            type: str
            choices: ['INPUT_CLOCK', 'SYSTEM_CLOCK']
          support_low_framerate_inputs:
            description:
              - Adjusts video input buffer for streams with very low video framerates. This is commonly set to enabled for music channels with less than one video frame per second.
            type: str
            choices: ['DISABLED', 'ENABLED']
          output_locking_settings:
            description:
              - Advanced output locking settings
            type: dict
            suboptions:
              epoch_locking_settings:
                description:
                  - Epoch Locking Settings
                type: dict
                suboptions:
                  custom_epoch:
                    description:
                      - Optional. Enter a value here to use a custom epoch, instead of the standard epoch (which started at 1970-01-01T00:00:00 UTC). Specify the start time of the custom epoch, in YYYY-MM-DDTHH:MM:SS in UTC. The time must be 2000-01-01T00:00:00 or later. Always set the MM:SS portion to 00:00.
                    type: str
                  jam_sync_time:
                    description:
                      - Optional. Enter a time for the jam sync. The default is midnight UTC. When epoch locking is enabled, MediaLive performs a daily jam sync on every output encode to ensure timecodes don't diverge from the wall clock. The jam sync applies only to encodes with frame rate of 29.97 or 59.94 FPS. To override, enter a time in HH:MM:SS in UTC. Always set the MM:SS portion to 00:00.
                    type: str
              pipeline_locking_settings:
                description:
                  - Pipeline Locking Settings
                type: dict
      motion_graphics_configuration:
        description:
          - Settings for motion graphics.
        type: dict
        suboptions:
          motion_graphics_insertion:
            description:
              - Motion Graphics Insertion
            type: str
            choices: ['DISABLED', 'ENABLED']
          motion_graphics_settings:
            description:
              - Motion Graphics Settings
            type: dict
            suboptions:
              html_motion_graphics_settings:
                description:
                  - Html Motion Graphics Settings
                type: dict
      nielsen_configuration:
        description:
          - Nielsen configuration settings.
        type: dict
        suboptions:
          distributor_id:
            description:
              - Enter the Distributor ID assigned to your organization by Nielsen.
            type: str
          nielsen_pcm_to_id3_tagging:
            description:
              - Enables Nielsen PCM to ID3 tagging
            type: str
            choices: ['DISABLED', 'ENABLED']
      output_groups:
        description:
          - Placeholder documentation for __listOfOutputGroup
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - Custom output group name optionally defined by the user.
            type: str
          output_group_settings:
            description:
              - Settings associated with the output group.
            type: dict
            suboptions:
              archive_group_settings:
                description:
                  - Archive Group Settings
                type: dict
                suboptions:
                  archive_cdn_settings:
                    description:
                      - Parameters that control interactions with the CDN.
                    type: dict
                    suboptions:
                      archive_s3_settings:
                        description:
                          - Archive S3 Settings
                        type: dict
                        suboptions:
                          canned_acl:
                            description:
                              - Specify the canned ACL to apply to each S3 request. Defaults to none.
                            type: str
                            choices:
                              - 'AUTHENTICATED_READ'
                              - 'BUCKET_OWNER_FULL_CONTROL'
                              - 'BUCKET_OWNER_READ'
                              - 'PUBLIC_READ'
                  destination:
                    description:
                      - A directory and base filename where archive files should be written.
                    type: dict
                    suboptions:
                      destination_ref_id:
                        description:
                          - Placeholder documentation for __string
                        type: str
                  rollover_interval:
                    description:
                      - Number of seconds to write to archive file before closing and starting a new one.
                    type: int
              frame_capture_group_settings:
                description:
                  - Frame Capture Group Settings
                type: dict
                suboptions:
                  destination:
                    description:
                      - The destination for the frame capture files. Either the URI for an Amazon S3 bucket and object, plus a file name prefix (for example, s3ssl://sportsDelivery/highlights/20180820/curling-) or the URI for a MediaStore container, plus a file name prefix (for example, mediastoressl://sportsDelivery/20180820/curling-). The final file names consist of the prefix from the destination field (for example, "curling-") + name modifier + the counter (5 digits, starting from 00001) + extension (which is always .jpg). For example, curling-low.00001.jpg
                    type: dict
                    suboptions:
                      destination_ref_id:
                        description:
                          - Placeholder documentation for __string
                        type: str
                  frame_capture_cdn_settings:
                    description:
                      - Parameters that control interactions with the CDN.
                    type: dict
                    suboptions:
                      frame_capture_s3_settings:
                        description:
                          - Frame Capture S3 Settings
                        type: dict
                        suboptions:
                          canned_acl:
                            description:
                              - Specify the canned ACL to apply to each S3 request. Defaults to none.
                            type: str
                            choices:
                              - 'AUTHENTICATED_READ'
                              - 'BUCKET_OWNER_FULL_CONTROL'
                              - 'BUCKET_OWNER_READ'
                              - 'PUBLIC_READ'
              hls_group_settings:
                description:
                  - Hls Group Settings
                type: dict
                suboptions:
                  ad_markers:
                    description:
                      - Choose one or more ad marker types to pass SCTE35 signals through to this group of Apple HLS outputs.
                    type: list
                    elements: str
                    choices: ['ADOBE', 'ELEMENTAL', 'ELEMENTAL_SCTE35']
                  base_url_content:
                    description:
                      - A partial URI prefix that will be prepended to each output in the media .m3u8 file. Can be used if base manifest is delivered from a different URL than the main .m3u8 file.
                    type: str
                  base_url_content1:
                    description:
                      - Optional. One value per output group. This field is required only if you are completing Base URL content A, and the downstream system has notified you that the media files for pipeline 1 of all outputs are in a location different from the media files for pipeline 0.
                    type: str
                  base_url_manifest:
                    description:
                      - A partial URI prefix that will be prepended to each output in the media .m3u8 file. Can be used if base manifest is delivered from a different URL than the main .m3u8 file.
                    type: str
                  base_url_manifest1:
                    description:
                      - Optional. One value per output group. Complete this field only if you are completing Base URL manifest A, and the downstream system has notified you that the child manifest files for pipeline 1 of all outputs are in a location different from the child manifest files for pipeline 0.
                    type: str
                  caption_language_mappings:
                    description:
                      - Mapping of up to 4 caption channels to caption languages. Is only meaningful if captionLanguageSetting is set to "insert".
                    type: list
                    elements: dict
                    suboptions:
                      caption_channel:
                        description:
                          - The closed caption channel being described by this CaptionLanguageMapping. Each channel mapping must have a unique channel number (maximum of 4)
                        type: int
                      language_code:
                        description:
                          - Three character ISO 639-2 language code (see http://www.loc.gov/standards/iso639-2)
                        type: str
                      language_description:
                        description:
                          - Textual description of language
                        type: str
                  caption_language_setting:
                    description:
                      - Applies only to 608 Embedded output captions. insert - Include CLOSED-CAPTIONS lines in the manifest. Specify at least one language in the CC1 Language Code field. One CLOSED-CAPTION line is added for each Language Code you specify. Make sure to specify the languages in the order in which they appear in the original source (if the source is embedded format) or the order of the caption selectors (if the source is other than embedded). Otherwise, languages in the manifest will not match up properly with the output captions. none - Include CLOSED-CAPTIONS=NONE line in the manifest. omit - Omit any CLOSED-CAPTIONS line from the manifest.
                    type: str
                    choices: ['INSERT', 'NONE', 'OMIT']
                  client_cache:
                    description:
                      - When set to "disabled", sets the #EXT-X-ALLOW-CACHE:no tag in the manifest, which prevents clients from saving media segments for later replay.
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  codec_specification:
                    description:
                      - Specification to use (RFC-6381 or the default RFC-4281) during m3u8 playlist generation.
                    type: str
                    choices: ['RFC_4281', 'RFC_6381']
                  constant_iv:
                    description:
                      - For use with encryptionType. This is a 128-bit, 16-byte hex value represented by a 32-character text string. If ivSource is set to "explicit" then this parameter is required and is used as the IV for encryption.
                    type: str
                  destination:
                    description:
                      - A directory or HTTP destination for the HLS segments, manifest files, and encryption keys (if enabled).
                    type: dict
                    suboptions:
                      destination_ref_id:
                        description:
                          - Placeholder documentation for __string
                        type: str
                  directory_structure:
                    description:
                      - Place segments in subdirectories.
                    type: str
                    choices: ['SINGLE_DIRECTORY', 'SUBDIRECTORY_PER_STREAM']
                  discontinuity_tags:
                    description:
                      - Specifies whether to insert EXT-X-DISCONTINUITY tags in the HLS child manifests for this output group. Typically, choose Insert because these tags are required in the manifest (according to the HLS specification) and serve an important purpose. Choose Never Insert only if the downstream system is doing real-time failover (without using the MediaLive automatic failover feature) and only if that downstream system has advised you to exclude the tags.
                    type: str
                    choices: ['INSERT', 'NEVER_INSERT']
                  encryption_type:
                    description:
                      - Encrypts the segments with the given encryption scheme. Exclude this parameter if no encryption is desired.
                    type: str
                    choices: ['AES128', 'SAMPLE_AES']
                  hls_cdn_settings:
                    description:
                      - Parameters that control interactions with the CDN.
                    type: dict
                    suboptions:
                      hls_akamai_settings:
                        description:
                          - Hls Akamai Settings
                        type: dict
                        suboptions:
                          connection_retry_interval:
                            description:
                              - Number of seconds to wait before retrying connection to the CDN if the connection is lost.
                            type: int
                          filecache_duration:
                            description:
                              - Size in seconds of file cache for streaming outputs.
                            type: int
                          http_transfer_mode:
                            description:
                              - Specify whether or not to use chunked transfer encoding to Akamai. User should contact Akamai to enable this feature.
                            type: str
                            choices: ['CHUNKED', 'NON_CHUNKED']
                          num_retries:
                            description:
                              - Number of retry attempts that will be made before the Live Event is put into an error state. Applies only if the CDN destination URI begins with "s3" or "mediastore". For other URIs, the value is always 3.
                            type: int
                          restart_delay:
                            description:
                              - If a streaming output fails, number of seconds to wait until a restart is initiated. A value of 0 means never restart.
                            type: int
                          salt:
                            description:
                              - Salt for authenticated Akamai.
                            type: str
                          token:
                            description:
                              - Token parameter for authenticated akamai. If not specified, _gda_ is used.
                            type: str
                      hls_basic_put_settings:
                        description:
                          - Hls Basic Put Settings
                        type: dict
                        suboptions:
                          connection_retry_interval:
                            description:
                              - Number of seconds to wait before retrying connection to the CDN if the connection is lost.
                            type: int
                          filecache_duration:
                            description:
                              - Size in seconds of file cache for streaming outputs.
                            type: int
                          num_retries:
                            description:
                              - Number of retry attempts that will be made before the Live Event is put into an error state. Applies only if the CDN destination URI begins with "s3" or "mediastore". For other URIs, the value is always 3.
                            type: int
                          restart_delay:
                            description:
                              - If a streaming output fails, number of seconds to wait until a restart is initiated. A value of 0 means never restart.
                            type: int
                      hls_media_store_settings:
                        description:
                          - Hls Media Store Settings
                        type: dict
                        suboptions:
                          connection_retry_interval:
                            description:
                              - Number of seconds to wait before retrying connection to the CDN if the connection is lost.
                            type: int
                          filecache_duration:
                            description:
                              - Size in seconds of file cache for streaming outputs.
                            type: int
                          media_store_storage_class:
                            description:
                              - When set to temporal, output files are stored in non-persistent memory for faster reading and writing.
                            type: str
                            choices: ['TEMPORAL']
                          num_retries:
                            description:
                              - Number of retry attempts that will be made before the Live Event is put into an error state. Applies only if the CDN destination URI begins with "s3" or "mediastore". For other URIs, the value is always 3.
                            type: int
                          restart_delay:
                            description:
                              - If a streaming output fails, number of seconds to wait until a restart is initiated. A value of 0 means never restart.
                            type: int
                      hls_s3_settings:
                        description:
                          - Hls S3 Settings
                        type: dict
                        suboptions:
                          canned_acl:
                            description:
                              - Specify the canned ACL to apply to each S3 request. Defaults to none.
                            type: str
                            choices: ['AUTHENTICATED_READ', 'BUCKET_OWNER_FULL_CONTROL', 'BUCKET_OWNER_READ', 'PUBLIC_READ']
                      hls_webdav_settings:
                        description:
                          - Hls Webdav Settings
                        type: dict
                        suboptions:
                          connection_retry_interval:
                            description:
                              - Number of seconds to wait before retrying connection to the CDN if the connection is lost.
                            type: int
                          filecache_duration:
                            description:
                              - Size in seconds of file cache for streaming outputs.
                            type: int
                          http_transfer_mode:
                            description:
                              - Specify whether or not to use chunked transfer encoding to WebDAV.
                            type: str
                            choices: ['CHUNKED', 'NON_CHUNKED']
                          num_retries:
                            description:
                              - Number of retry attempts that will be made before the Live Event is put into an error state. Applies only if the CDN destination URI begins with "s3" or "mediastore". For other URIs, the value is always 3.
                            type: int
                          restart_delay:
                            description:
                              - If a streaming output fails, number of seconds to wait until a restart is initiated. A value of 0 means never restart.
                            type: int
                  hls_id3_segment_tagging:
                    description:
                      - State of HLS ID3 Segment Tagging
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  i_frame_only_playlists:
                    description:
                      - DISABLED - Do not create an I-frame-only manifest, but do create the master and media manifests (according to the Output Selection field). STANDARD - Create an I-frame-only manifest for each output that contains video, as well as the other manifests (according to the Output Selection field). The I-frame manifest contains a #EXT-X-I-FRAMES-ONLY tag to indicate it is I-frame only, and one or more #EXT-X-BYTERANGE entries identifying the I-frame position. For example, #EXT-X-BYTERANGE:160364@1461888"
                    type: str
                    choices: ['DISABLED', 'STANDARD']
                  incomplete_segment_behavior:
                    description:
                      - Specifies whether to include the final (incomplete) segment in the media output when the pipeline stops producing output because of a channel stop, a channel pause or a loss of input to the pipeline. Auto means that MediaLive decides whether to include the final segment, depending on the channel class and the types of output groups. Suppress means to never include the incomplete segment. We recommend you choose Auto and let MediaLive control the behavior.
                    type: str
                    choices: ['AUTO', 'SUPPRESS']
                  index_n_segments:
                    description:
                      - Applies only if Mode field is LIVE. Specifies the maximum number of segments in the media manifest file. After this maximum, older segments are removed from the media manifest. This number must be smaller than the number in the Keep Segments field.
                    type: int
                  input_loss_action:
                    description:
                      - Parameter that control output group behavior on input loss.
                    type: str
                    choices: ['EMIT_OUTPUT', 'PAUSE_OUTPUT']
                  iv_in_manifest:
                    description:
                      - For use with encryptionType. The IV (Initialization Vector) is a 128-bit number used in conjunction with the key for encrypting blocks. If set to "include", IV is listed in the manifest, otherwise the IV is not in the manifest.
                    type: str
                    choices: ['EXCLUDE', 'INCLUDE']
                  iv_source:
                    description:
                      - For use with encryptionType. The IV (Initialization Vector) is a 128-bit number used in conjunction with the key for encrypting blocks. If this setting is "followsSegmentNumber", it will cause the IV to change every segment (to match the segment number). If this is set to "explicit", you must enter a constantIv value.
                    type: str
                    choices: ['EXPLICIT', 'FOLLOWS_SEGMENT_NUMBER']
                  keep_segments:
                    description:
                      - Applies only if Mode field is LIVE. Specifies the number of media segments to retain in the destination directory. This number should be bigger than indexNSegments (Num segments). We recommend (value = (2 x indexNsegments) + 1). If this "keep segments" number is too low, the following might happen - the player is still reading a media manifest file that lists this segment, but that segment has been removed from the destination directory (as directed by indexNSegments). This situation would result in a 404 HTTP error on the player.
                    type: int
                  key_format:
                    description:
                      - The value specifies how the key is represented in the resource identified by the URI. If parameter is absent, an implicit value of "identity" is used. A reverse DNS string can also be given.
                    type: str
                  key_format_versions:
                    description:
                      - Either a single positive integer version value or a slash delimited list of version values (1/2/3).
                    type: str
                  key_provider_settings:
                    description:
                      - The key provider settings.
                    type: dict
                    suboptions:
                      static_key_settings:
                        description:
                          - Static Key Settings
                        type: dict
                        suboptions:
                          key_provider_server:
                            description:
                              - The URL of the license server used for protecting content.
                            type: dict
                            suboptions:
                              password_param:
                                description:
                                  - key used to extract the password from EC2 Parameter store
                                type: str
                              uri:
                                description:
                                  - Uniform Resource Identifier - This should be a path to a file accessible to the Live system (eg. a http:// URI) depending on the output type. For example, a RTMP destination should have a uri simliar to "rtmp://fmsserver/live".
                                type: str
                              username:
                                description:
                                  - Documentation update needed
                                type: str
                          static_key_value:
                            description:
                              - Static key value as a 32 character hexadecimal string.
                            type: str
                  manifest_compression:
                    description:
                      - When set to gzip, compresses HLS playlist.
                    type: str
                    choices: ['GZIP', 'NONE']
                  manifest_duration_format:
                    description:
                      - Indicates whether the output manifest should use floating point values for segment duration.
                    type: str
                    choices: ['FLOATING_POINT', 'INTEGER']
                  min_segment_length:
                    description:
                      - When set, minimumSegmentLength is enforced by looking ahead and back within the specified range for a nearby avail and extending the segment size if needed.
                    type: int
                  mode:
                    description:
                      - If "vod", all segments are indexed and kept permanently in the destination and manifest. If "live", only the number segments specified in keepSegments and indexNSegments are kept; newer segments replace older segments, which may prevent players from rewinding all the way to the beginning of the event. VOD mode uses HLS EXT-X-PLAYLIST-TYPE of EVENT while the channel is running, converting it to a "VOD" type manifest on completion of the stream.
                    type: str
                    choices: ['LIVE', 'VOD']
                  output_selection:
                    description:
                      - MANIFESTS_AND_SEGMENTS - The master manifest (and media manifests, if created) and all segments are created. SEGMENTS_ONLY - No manifests are created; just segments. VARIANT_MANIFESTS_AND_SEGMENTS - Media manifests and segments are created, but not the master manifest.
                    type: str
                    choices: ['MANIFESTS_AND_SEGMENTS', 'SEGMENTS_ONLY', 'VARIANT_MANIFESTS_AND_SEGMENTS']
                  program_date_time:
                    description:
                      - Includes or excludes the EXT-X-PROGRAM-DATE-TIME tag in .m3u8 manifest files. The value is calculated as follows - either the program date and time are initialized using the input timecode source, or the time is initialized using the input timecode source and the date is initialized using the timestampOffset.
                    type: str
                    choices: ['EXCLUDE', 'INCLUDE']
                  program_date_time_clock:
                    description:
                      - Specifies the source of the program date time. If "systemClock" is selected, the time will be the current time of the system. If "initializeFromOutputTimecode" is selected, the time will be initialized from the first output timecode. If "systemClock" is selected, the time will be the current time of the system.
                    type: str
                    choices: ['INITIALIZE_FROM_OUTPUT_TIMECODE', 'SYSTEM_CLOCK']
                  program_date_time_period:
                    description:
                      - Period of insertion of EXT-X-PROGRAM-DATE-TIME entry, in seconds.
                    type: int
                  redundant_manifest:
                    description:
                      - ENABLED - The master manifest (.m3u8 file) for each pipeline includes information about both pipelines, first its own media files, then the same for the other pipeline. This feature allows playout device that support stale manifest detection to switch from one manifest to the other, when the current manifest seems to be stale. There are still two destinations and two master manifests, but both master manifests reference the media files from both pipelines. DISABLED - The master manifest (.m3u8 file) for each pipeline includes information about its own pipeline only. For an HLS output group with MediaPackage as the destination, the DISABLED behavior is always followed. MediaPackage regenerates the manifests it serves to players so a redundant manifest from MediaLive is irrelevant.
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  segment_length:
                    description:
                      - Length of MPEG-2 Transport Stream segments to create (in seconds). Note that segments will end on the next keyframe after this number of seconds, so actual segment length may be longer.
                    type: int
                  segmentation_mode:
                    description:
                      - useInputSegmentation has been deprecated. The configured segment size is always used.
                    type: str
                    choices: ['USE_INPUT_SEGMENTATION', 'USE_SEGMENT_DURATION']
                  segments_per_subdirectory:
                    description:
                      - Number of segments to write to a subdirectory before starting a new one. directoryStructure must be subdirectoryPerStream for this setting to have an effect.
                    type: int
                  stream_inf_resolution:
                    description:
                      - Include or exclude RESOLUTION attribute for video in EXT-X-STREAM-INF tag of variant manifest.
                    type: str
                    choices: ['EXCLUDE', 'INCLUDE']
                  timed_metadata_id3_frame:
                    description:
                      - Indicates ID3 frame that has the timecode.
                    type: str
                    choices: ['NONE', 'PRIV', 'TDRL']
                  timed_metadata_id3_period:
                    description:
                      - Timed Metadata interval in seconds.
                    type: int
                  timestamp_delta_milliseconds:
                    description:
                      - Provides an extra millisecond delta offset to fine tune the timestamps.
                    type: int
                  ts_file_mode:
                    description:
                      - SEGMENTED_FILES - Emit the program as segments - multiple .ts media files. SINGLE_FILE - Applies only if Mode field is VOD. Emit the program as a single .ts media file. The media manifest includes #EXT-X-BYTERANGE tags to index segments for playback. A typical use for this value is when sending the output to AWS Elemental MediaConvert, which can accept only a single media file. Playback while the channel is running is not guaranteed due to HTTP server caching.
                    type: str
                    choices: ['SEGMENTED_FILES', 'SINGLE_FILE']
              media_package_group_settings:
                description:
                  - Media Package Group Settings
                type: dict
                suboptions:
                  destination:
                    description:
                      - MediaPackage channel destination.
                    type: dict
                    suboptions:
                      destination_ref_id:
                        description:
                          - Placeholder documentation for __string
                        type: str
              ms_smooth_group_settings:
                description:
                  - Ms Smooth Group Settings
                type: dict
                suboptions:
                  acquisition_point_id:
                    description:
                      - The value of the id attribute for the Acquisition Point element. This must match the value of the acquisition point identity attribute in the custom preset file. This is used to associate incoming content with this MS Smooth output.
                    type: str
                  audio_only_timecode_control:
                    description:
                      - If set to passthrough for an audio-only MS Smooth output, the fragment absolute time will be set to the current timecode. This option does not write timecodes to the audio elementary stream.
                    type: str
                    choices: ['PASSTHROUGH', 'USE_CONFIGURED_CLOCK']
                  certificate_mode:
                    description:
                      - If set to verifyAuthenticity, verify the https certificate chain to a trusted Certificate Authority (CA). This will cause https outputs to self-signed certificates to fail.
                    type: str
                    choices: ['SELF_SIGNED', 'VERIFY_AUTHENTICITY']
                  connection_retry_interval:
                    description:
                      - Number of seconds to wait before retrying connection to the IIS server if the connection is lost. Content will be cached during this time and the cache will be be delivered to the IIS server once the connection is re-established.
                    type: int
                  destination:
                    description:
                      - Smooth Streaming publish point on an IIS server. Elemental Live acts as a "Push" encoder to IIS.
                    type: dict
                    suboptions:
                      destination_ref_id:
                        description:
                          - Placeholder documentation for __string
                        type: str
                  event_id:
                    description:
                      - MS Smooth event ID to be sent to the IIS server. Should only be specified if eventIdMode is set to useConfigured.
                    type: str
                  event_id_mode:
                    description:
                      - Specifies whether or not to send an event ID to the IIS server. If no event ID is sent and the same Live Event is used without changing the publishing point, clients might see cached video from the previous run. Options - "useConfigured" - use the value provided in eventId - "useTimestamp" - generate and send an event ID based on the current timestamp - "noEventId" - do not send an event ID to the IIS server.
                    type: str
                    choices: ['NO_EVENT_ID', 'USE_CONFIGURED', 'USE_TIMESTAMP']
                  event_stop_behavior:
                    description:
                      - When set to sendEos, send EOS signal to IIS server when stopping the event
                    type: str
                    choices: ['NONE', 'SEND_EOS']
                  filecache_duration:
                    description:
                      - Size in seconds of file cache for streaming outputs.
                    type: int
                  fragment_length:
                    description:
                      - Length of mp4 fragments to generate (in seconds). Fragment length must be compatible with GOP size and framerate.
                    type: int
                  input_loss_action:
                    description:
                      - Parameter that control output group behavior on input loss.
                    type: str
                    choices: ['EMIT_OUTPUT', 'PAUSE_OUTPUT']
                  num_retries:
                    description:
                      - Number of retry attempts.
                    type: int
                  restart_delay:
                    description:
                      - Number of seconds before initiating a restart due to output failure, due to exhausting the numRetries on one segment, or exceeding filecacheDuration.
                    type: int
                  segmentation_mode:
                    description:
                      - useInputSegmentation has been deprecated. The configured segment size is always used.
                    type: str
                    choices: ['USE_INPUT_SEGMENTATION', 'USE_SEGMENT_DURATION']
                  send_delay_ms:
                    description:
                      - Number of milliseconds to delay the output from the second pipeline.
                    type: int
                  sparse_track_type:
                    description:
                      - If set to scte35, use incoming SCTE-35 messages to generate a sparse track in this group of MS-Smooth outputs.
                    type: str
                    choices: ['NONE', 'SCTE_35', 'SCTE_35_WITHOUT_SEGMENTATION']
                  stream_manifest_behavior:
                    description:
                      - When set to send, send stream manifest so publishing point doesn't start until all streams start.
                    type: str
                    choices: ['DO_NOT_SEND', 'SEND']
                  timestamp_offset:
                    description:
                      - Timestamp offset for the event. Only used if timestampOffsetMode is set to useConfiguredOffset.
                    type: str
                  timestamp_offset_mode:
                    description:
                      - Type of timestamp date offset to use. useEventStartDate - Use the date the event was started as the offset, useConfiguredOffset - Use an explicitly configured date as the offset
                    type: str
                    choices: ['USE_CONFIGURED_OFFSET', 'USE_EVENT_START_DATE']
              multiplex_group_settings:
                description:
                  - Multiplex Group Settings
                type: dict
              rtmp_group_settings:
                description:
                  - Rtmp Group Settings
                type: dict
                suboptions:
                  ad_markers:
                    description:
                      - Choose the ad marker type for this output group. MediaLive will create a message based on the content of each SCTE-35 message, format it for that marker type, and insert it in the datastream.
                    type: list
                    elements: str
                    choices: ['ON_CUE_POINT_SCTE35']
                  AuthenticationScheme:
                    description:
                      - Authentication scheme to use when connecting with CDN
                    type: str
                    choices: ['AKAMAI', 'COMMON']
                  CacheFullBehavior:
                    description:
                      - Controls behavior when content cache fills up
                    type: str
                    choices: ['DISCONNECT_IMMEDIATELY', 'WAIT_FOR_SERVER']
                  CacheLength:
                    description:
                      - Cache length, in seconds, is used to calculate buffer size
                    type: int
                  CaptionData:
                    description:
                      - Controls the types of data that passes to onCaptionInfo outputs. If set to 'all' then 608 and 708 carried DTVCC data will be passed. If set to 'field1AndField2608' then DTVCC data will be stripped out, but 608 data from both fields will be passed. If set to 'field1608' then only the data carried in 608 from field 1 video will be passed.
                    type: str
                    choices: ['ALL', 'FIELD1_608', 'FIELD1_AND_FIELD2_608']
                  InputLossAction:
                    description:
                      - Controls the behavior of this RTMP group if input becomes unavailable. - emitOutput Emit a slate until input returns. - pauseOutput Stop transmitting data until input returns. This does not close the underlying RTMP connection.
                    type: str
                    choices: ['EMIT_OUTPUT', 'PAUSE_OUTPUT']
                  RestartDelay:
                    description:
                      - If a streaming output fails, number of seconds to wait until a restart is initiated. A value of 0 means never restart.
                    type: int
                  IncludeFillerNalUnits:
                    description:
                      - Applies only to H.264 outputs. Specifies whether to include the filler NAL units in the output. Keep the default value (AUTO) unless you need to reference the filler NAL units in custom downstream systems. INCLUDE - Include filler NAL units in the output. DROP - Remove filler NAL units from the output. AUTO - Remove filler NAL units from the output, unless the output frame rate is 50 or 60 fps, and the output group is either a DASH or HLS group. In that case, include the filler NAL units in the output.
                    type: str
                    choices: ['AUTO', 'DROP', 'INCLUDE']
              udp_group_settings:
                description:
                  - Udp Group Settings
                type: dict
                suboptions:
                  input_loss_action:
                    description:
                      - Specifies behavior of last resort when input video is lost, and no more backup inputs are available. When dropTs is selected the entire transport stream will stop being emitted. When dropProgram is selected only the affected program(s) will stop being emitted.
                    type: str
                    choices: ['DROP_PROGRAM', 'DROP_TS', 'EMIT_PROGRAM']
                  timed_metadata_id3_frame:
                    description:
                      - Indicates ID3 frame that has the timecode.
                    type: str
                    choices: ['NONE', 'PRIV', 'TDRL']
                  timed_metadata_id3_period:
                    description:
                      - Timed Metadata interval in seconds.
                    type: int
              cmaf_ingest_group_settings:
                description:
                  - Cmaf Ingest Group Settings
                type: dict
                suboptions:
                  destination:
                    description:
                      - A directory or HTTP destination for the CMAF Ingest segments.
                    type: dict
                    suboptions:
                      destination_ref_id:
                        description:
                          - Placeholder documentation for __string
                        type: str
                  nielsen_id3_behavior:
                    description:
                      - If set to passthrough, Nielsen inaudible tones for media tracking will be detected in the input audio and an equivalent ID3 tag will be inserted in the output.
                    type: str
                    choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                  scte35_type:
                    description:
                    type: str
                    choices: ['NONE', 'SCTE_35_WITHOUT_SEGMENTATION']
                  segment_length:
                    description:
                      - Length of CMAF segments to create (in seconds or milliseconds, depending on the segment length mode). Note that segments will end on the next keyframe after this number of seconds, so actual segment length may be longer.
                    type: int
                  segment_length_units:
                    description:
                      - Specifies the units for the segment length.
                    type: str
                    choices: ['MILLISECONDS', 'SECONDS']
                  send_delay_ms:
                    description:
                      - Number of milliseconds to delay the output from the second pipeline.
                    type: int
                  klv_behavior:
                    description:
                      - If set to passthrough, passes any KLV data from the input source to this output.
                    type: str
                    choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                  klv_name_modifier:
                    description:
                      - Applies a string to the KLV output file names.
                    type: str
                  nielsen_id3_name_modifier:
                    description:
                      - Applies a string to the Nielsen ID3 output file names.
                    type: str
                  scte35_name_modifier:
                    description:
                      - Applies a string to the SCTE-35 output file names.
                    type: str
                  id3_behavior:
                    description:
                      - If set to passthrough, passes any ID3 metadata from the input source to this output.
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  id3_name_modifier:
                    description:
                      - Applies a string to the ID3 output file names.
                    type: str
                  caption_language_mappings:
                    description:
                      - Mapping of up to 4 caption channels to caption languages. Is only meaningful if captionLanguageSetting is set to "insert".
                    type: list
                    elements: dict
                    suboptions:
                      caption_channel:
                        description:
                          - The closed caption channel being described by this CaptionLanguageMapping. Each channel mapping must have a unique channel number (maximum of 4)
                        type: int
                      language_code:
                        description:
                          - Three character ISO 639-2 language code (see http://www.loc.gov/standards/iso639-2)
                        type: str
                  timed_metadata_id3_frame:
                    description:
                      - Indicates ID3 frame that has the timecode.
                    type: str
                    choices: ['NONE', 'PRIV', 'TDRL']
                  timed_metadata_id3_period:
                    description:
                      - Timed Metadata interval in seconds.
                    type: int
                  timed_metadata_passthrough:
                    description:
                      - If set to passthrough, passes any timed metadata from the input source to this output.
                    type: str
                    choices: ['DISABLED', 'ENABLED']
              srt_group_settings:
                description:
                  - Srt Group Settings
                type: dict
                suboptions:
                  input_loss_action:
                    description:
                      - Specifies behavior of last resort when input video is lost, and no more backup inputs are available. When dropTs is selected the entire transport stream will stop being emitted. When dropProgram is selected only the affected program(s) will stop being emitted.
                    type: str
                    choices: ['DROP_PROGRAM', 'DROP_TS', 'EMIT_PROGRAM']
          outputs:
            description:
              - The array of Output specifications
            type: list
            elements: dict
            suboptions:
              audio_description_names:
                description:
                  - The names of the AudioDescriptions used as audio sources for this output.
                type: list
                elements: str
              caption_description_names:
                description:
                  - The names of the CaptionDescriptions used as caption sources for this output.
                type: list
                elements: str
              output_name:
                description:
                  - The name used to identify an output.
                type: str
              output_settings:
                description:
                  - Output Settings
                type: dict
                suboptions:
                  archive_output_settings:
                    description:
                      - Archive Output Settings
                    type: dict
                    suboptions:
                      container_settings:
                        description:
                          - Settings specific to the container type of the file.
                        type: dict
                        suboptions:
                          m2ts_settings:
                            description:
                              - M2ts Settings
                            type: dict
                            suboptions:
                              absent_input_audio_behavior:
                                description:
                                  - When set to drop, output audio streams will be removed from the program if the selected input audio stream is removed from the input. This allows the output audio configuration to dynamically change based on input configuration. If this is set to encodeSilence, all output audio streams will output encoded silence when not connected to an active input stream.
                                type: str
                                choices: ['DROP', 'ENCODE_SILENCE']
                              arib:
                                description:
                                  - When set to enabled, uses ARIB standard for DVB subtitles.
                                type: str
                                choices: ['DISABLED', 'ENABLED']
                              arib_captions_pid:
                                description:
                                  - Packet Identifier (PID) for ARIB Captions in the transport stream. Can be entered as a decimal or hexadecimal value. Valid values are 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              arib_captions_pid_control:
                                description:
                                  - If set to auto, pid number used for ARIB Captions will be auto-selected from unused pids. If set to useConfigured, ARIB Captions will be on the configured pid number.
                                type: str
                                choices: ['AUTO', 'USE_CONFIGURED']
                              audio_buffer_model:
                                description:
                                  - When set to dvb, uses DVB buffer model for Dolby Digital audio. When set to atsc, uses ATSC model.
                                type: str
                                choices: ['ATSC', 'DVB']
                              audio_frames_per_pes:
                                description:
                                  - The number of audio frames to insert for each PES packet.
                                type: int
                                      
                              audio_pids:
                                description:
                                  - Packet Identifier (PID) of the elementary audio stream(s) in the transport stream. Multiple values are accepted, and can be entered in ranges and/or by comma separation. Can be entered as decimal or hexadecimal values. Each PID specified must be in the range of 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              audio_stream_type:
                                description:
                                  - When set to atsc, uses stream type = 0x81 for AC3 and stream type = 0x87 for EAC3. When set to dvb, uses stream type = 0x06.
                                type: str
                                choices: ['ATSC', 'DVB']
                              bitrate:
                                description:
                                  - The output bitrate of the transport stream in bits per second. Setting to 0 lets the muxer automatically determine the appropriate bitrate.
                                type: int
                              buffer_model:
                                description:
                                  - If set to multiplex, use multiplex buffer model for accurate interleaving. Setting to none can lead to lower latency, but low-memory devices may not be able to play back the stream without interruptions.
                                type: str
                                choices: ['MULTIPLEX', 'NONE']
                              cc_descriptor:
                                description:
                                  - When set to enabled, generates captionServiceDescriptor in PMT.
                                type: str
                                choices: ['DISABLED', 'ENABLED']
                              dvb_nit_settings:
                                description:
                                  - Inserts DVB Network Information Table (NIT) at the specified table repetition interval.
                                type: dict
                                suboptions:
                                  network_id:
                                    description:
                                      - The numeric value placed in the Network Information Table (NIT).
                                    type: int
                                  network_name:
                                    description:
                                      - The network name text placed in the networkNameDescriptor inside the Network Information Table (NIT). Maximum length is 256 characters.
                                    type: str
                                  rep_interval:
                                    description:
                                      - The number of milliseconds between instances of this table in the output transport stream.
                                    type: int
                              dvb_sdt_settings:
                                description:
                                  - Inserts DVB Service Description Table (SDT) at the specified table repetition interval.
                                type: dict
                                suboptions:
                                  output_sdt:
                                    description:
                                      - Selects method of SDT insertion. "sdtFollow" sets the SDT to follow the input SDT. "sdtFollowIfPresent" makes the output SDT follow the input SDT when present, otherwise it will fall back on the user-defined values. "sdtManual" means the user will enter the SDT in the provided parameters. "sdtNone" means no SDT will be output.
                                    type: str
                                    choices: ['SDT_FOLLOW', 'SDT_FOLLOW_IF_PRESENT', 'SDT_MANUAL', 'SDT_NONE']
                                  rep_interval:
                                    description:
                                      - The number of milliseconds between instances of this table in the output transport stream.
                                    type: int
                                  service_name:
                                    description:
                                      - The service name placed in the serviceDescriptor in the Service Description Table (SDT). Maximum length is 256 characters.
                                    type: str
                                  service_provider_name:
                                    description:
                                      - The service provider name placed in the serviceDescriptor in the Service Description Table (SDT). Maximum length is 256 characters.
                                    type: str
                              dvb_sub_pids:
                                description:
                                  - Packet Identifier (PID) for input source DVB Subtitle data to this output. Multiple values are accepted, and can be entered in ranges and/or by comma separation. Can be entered as decimal or hexadecimal values. Each PID specified must be in the range of 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              dvb_tdt_settings:
                                description:
                                  - Inserts DVB Time and Date Table (TDT) at the specified table repetition interval.
                                type: dict
                                suboptions:
                                  rep_interval:
                                    description:
                                      - The number of milliseconds between instances of this table in the output transport stream.
                                    type: int
                              dvb_teletext_pid:
                                description:
                                  - Packet Identifier (PID) for input source DVB Teletext data to this output. Can be entered as a decimal or hexadecimal value. Valid values are 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              ebif:
                                description:
                                  - If set to passthrough, passes any EBIF data from the input source to this output.
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              ebp_audio_interval:
                                description:
                                  - When videoAndFixedIntervals is selected, audio EBP markers will be added to partitions 3 and 4. The interval between these additional markers will be fixed, and will be slightly shorter than the video EBP marker interval. Only available when EBP Cablelabs segmentation markers are selected. Partitions 1 and 2 will always follow the video interval.
                                type: str
                                choices: ['VIDEO_AND_FIXED_INTERVALS', 'VIDEO_INTERVAL']
                              ebp_lookahead_ms:
                                description:
                                  - When set, enforces that Enhanced Binary Partitioning (EBP) is used for this output. If set to ebpLookaheadMs, partitions will be added to the stream to allow for the downstream system to perform time-shifting (e.g. to delay the stream by 10s), without interrupting the program at the partition.
                                type: int
                              ebp_placement:
                                description:
                                  - Controls placement of EBP on Audio PIDs. If set to videoAndAudioPids, EBP markers will be placed on both video and audio PIDs. If set to videoPid, EBP markers will be placed on only the video PID.
                                type: str
                                choices: ['VIDEO_AND_AUDIO_PIDS', 'VIDEO_PID']
                              ecm_pid:
                                description:
                                  - This field is unused and deprecated.
                                type: str
                              es_rate_in_pes:
                                description:
                                  - Include or exclude the ES Rate field in the PES header.
                                type: str
                                choices: ['EXCLUDE', 'INCLUDE']
                              etv_platform_pid:
                                description:
                                  - Packet Identifier (PID) for input source ETV Platform data to this output. Can be entered as a decimal or hexadecimal value. Valid values are 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              etv_signal_pid:
                                description:
                                  - Packet Identifier (PID) for input source ETV Signal data to this output. Can be entered as a decimal or hexadecimal value. Valid values are 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              fragment_time:
                                description:
                                  - The length in seconds of each fragment. Only used with EBP markers.
                                type: float
                              klv:
                                description:
                                  - If set to passthrough, passes any KLV data from the input source to this output.
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              klv_data_pids:
                                description:
                                  - Packet Identifier (PID) for input source KLV data to this output. Multiple values are accepted, and can be entered in ranges and/or by comma separation. Can be entered as decimal or hexadecimal values. Each PID specified must be in the range of 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              nielsen_id3_behavior:
                                description:
                                  - If set to passthrough, Nielsen inaudible tones for media tracking will be detected in the input audio and an equivalent ID3 tag will be inserted in the output.
                                type: str
                                choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                              null_packet_bitrate:
                                description:
                                  - Value in bits per second of extra null packets to insert into the transport stream. This can be used if a downstream encryption system requires specific minimum bitrate.
                                type: float
                              pat_interval:
                                description:
                                  - The number of milliseconds between instances of this table in the output transport stream. Valid values are 0, 10..1000.
                                type: int
                              pcr_control:
                                description:
                                  - When set to pcrEveryPesPacket, a Program Clock Reference value is inserted for every Packetized Elementary Stream (PES) header. This parameter is effective only when the PCR PID is the same as the video or audio elementary stream.
                                type: str
                                choices: ['CONFIGURED_PCR_PERIOD', 'PCR_EVERY_PES_PACKET']
                              pat_period:
                                description:
                                  - The number of milliseconds between instances of this table in the output transport stream. Valid values are 0, 10..1000.
                                type: int
                              pcr_pid:
                                description:
                                  - Packet Identifier (PID) of the Program Clock Reference (PCR) in the transport stream. When no value is given, the encoder will assign the same value as the Video PID. Can be entered as a decimal or hexadecimal value. Valid values are 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              pmt_interval:
                                description:
                                  - The number of milliseconds between instances of this table in the output transport stream. Valid values are 0, 10..1000.
                                type: int
                              pmt_pid:
                                description:
                                  - Packet Identifier (PID) for the Program Map Table (PMT) in the transport stream. Can be entered as a decimal or hexadecimal value. Valid values are 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              program_num:
                                description:
                                  - The value of the program number field in the Program Map Table.
                                type: int
                              rate_mode:
                                description:
                                  - When set to vbr, does not insert null packets into transport stream to fill specified bitrate. The bitrate setting acts as the maximum bitrate when vbr is set.
                                type: str
                                choices: ['CBR', 'VBR']
                              scte27_pids:
                                description:
                                  - Packet Identifier (PID) for input source SCTE-27 data to this output. Multiple values are accepted, and can be entered in ranges and/or by comma separation. Can be entered as decimal or hexadecimal values. Each PID specified must be in the range of 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              scte35_control:
                                description:
                                  - Optionally pass SCTE-35 signals from the input source to this output.
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              scte35_pid:
                                description:
                                  - Packet Identifier (PID) of the SCTE-35 stream in the transport stream. Can be entered as a decimal or hexadecimal value. Valid values are 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              segmentation_markers:
                                description:
                                  - Inserts segmentation markers at each segmentation_time period. rai_segstart sets the Random Access Indicator bit in the adaptation field. rai_adapt sets the RAI bit and adds the current timecode in the private data bytes. psi_segstart inserts PAT and PMT tables at the start of segments. ebp adds Encoder Boundary Point information to the adaptation field as per OpenCable specification OC-SP-EBP-I01-130118. ebp_legacy adds Encoder Boundary Point information to the adaptation field using a legacy proprietary format.
                                type: str
                                choices: ['EBP', 'EBP_LEGACY', 'NONE', 'PSI_SEGSTART', 'RAI_ADAPT', 'RAI_SEGSTART']
                              segmentation_style:
                                description:
                                  - The segmentation style parameter controls how segmentation markers are inserted into the transport stream. With avails, it is possible that segments may be truncated, which can influence where future segmentation markers are inserted. When a segmentation style of "resetCadence" is selected and a segment is truncated due to an avail, we will reset the segmentation cadence. This means the subsequent segment will have a duration of $segmentationTime seconds. When a segmentation style of "maintainCadence" is selected and a segment is truncated due to an avail, we will not reset the segmentation cadence. This means the subsequent segment will likely be truncated as well. However, all segments after that will have a duration of $segmentationTime seconds. Note that EBP lookahead is a slight exception to this rule.
                                type: str
                                choices: ['MAINTAIN_CADENCE', 'RESET_CADENCE']
                              segmentation_time:
                                description:
                                  - The length in seconds of each segment. Required unless markers is set to None_.
                                type: float
                              timed_metadata_behavior:
                                description:
                                  - When set to passthrough, timed metadata will be passed through from input to output.
                                type: str
                                choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                              timed_metadata_pid:
                                description:
                                  - Packet Identifier (PID) of the timed metadata stream in the transport stream. Can be entered as a decimal or hexadecimal value. Valid values are 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              transport_stream_id:
                                description:
                                  - The value of the transport stream ID field in the Program Map Table.
                                type: int
                              video_pid:
                                description:
                                  - Packet Identifier (PID) of the elementary video stream in the transport stream. Can be entered as a decimal or hexadecimal value. Valid values are 32 (or 0x20)..8182 (or 0x1ff6).
                                type: str
                              scte35_preroll_pullup_milliseconds:
                                description:
                                  - Adjusts the timing of SCTE-35 messages to account for delays introduced by ad insertion. Must be a positive number less than 1000.
                                type: float
                          raw_settings:
                            description:
                              - Raw Settings
                            type: dict
                      extension:
                        description:
                          - Output file extension. If excluded, this will be auto-selected from the container type.
                        type: str
                      name_modifier:
                        description:
                          - String concatenated to the end of the destination filename. Required for multiple outputs of the same type.
                        type: str
                  frame_capture_output_settings:
                    description:
                      - Frame Capture Output Settings
                    type: dict
                    suboptions:
                      name_modifier:
                        description:
                          - Required if there are multiple Frame Capture outputs that have the same output path. This modifier forms part of the output file name.
                        type: str
                  hls_output_settings:
                    description:
                      - Hls Output Settings
                    type: dict
                    suboptions:
                      h265_packaging_type:
                        description:
                          - Only applicable when this output is referencing an H.265 video description. Specifies whether MP4 segments should be packaged as HEV1 or HVC1.
                        type: str
                        choices: ['HEV1', 'HVC1']
                      hls_settings:
                        description:
                          - Hls Settings
                        type: dict
                        suboptions:
                          audio_only_hls_settings:
                            description:
                              - Audio Only Hls Settings
                            type: dict
                            suboptions:
                              audio_group_id:
                                description:
                                  - Specifies the group to which the audio Rendition belongs.
                                type: str
                              audio_only_image:
                                description:
                                  - Optional. Specifies an image to display when the stream is playing audio only content.
                                type: dict
                                suboptions:
                                  password_param:
                                    description:
                                      - key used to extract the password from EC2 Parameter store
                                    type: str
                                  uri:
                                    description:
                                      - Uniform Resource Identifier - This should be a path to a file accessible to the Live system (eg. a http:// URI) depending on the output type. For example, a RTMP destination should have a uri simliar to "rtmp://fmsserver/live".
                                    type: str
                                  username:
                                    description:
                                      - Documentation update needed
                                    type: str
                              audio_track_type:
                                description:
                                  - Four types of audio-only tracks are supported. Audio-Only Variant Stream The client can play this audio-only stream instead of video in low-bandwidth scenarios. Represented as an EXT-X-STREAM-INF in the HLS manifest. Alternate Audio, Auto Select, Default Alternate rendition that the client should try to play back by default. Represented as an EXT-X-MEDIA in the HLS manifest with DEFAULT=YES, AUTOSELECT=YES Alternate Audio, Auto Select, Not Default Alternate rendition that the client may try to play back by default. Represented as an EXT-X-MEDIA in the HLS manifest with DEFAULT=NO, AUTOSELECT=YES Alternate Audio, not Auto Select Alternate rendition that the client will not try to play back by default. Represented as an EXT-X-MEDIA in the HLS manifest with DEFAULT=NO, AUTOSELECT=NO
                                type: str
                                choices:
                                  - 'ALTERNATE_AUDIO_AUTO_SELECT'
                                  - 'ALTERNATE_AUDIO_AUTO_SELECT_DEFAULT'
                                  - 'ALTERNATE_AUDIO_NOT_AUTO_SELECT'
                                  - 'AUDIO_ONLY_VARIANT_STREAM'
                              segment_type:
                                description:
                                  - Specifies the segment type.
                                type: str
                                choices: ['AAC', 'FMP4']
                          fmp4_hls_settings:
                            description:
                              - Fmp4 Hls Settings
                            type: dict
                            suboptions:
                              audio_rendition_sets:
                                description:
                                  - List all the audio groups that are used with the video output stream. Input all the audio GROUP-IDs that are associated to the video, separate by ','.
                                type: str
                              nielsen_id3_behavior:
                                description:
                                  - If set to passthrough, Nielsen inaudible tones for media tracking will be detected in the input audio and an equivalent ID3 tag will be inserted in the output.
                                type: str
                                choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                              timed_metadata_behavior:
                                description:
                                  - When set to passthrough, timed metadata is passed through from input to output.
                                type: str
                                choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                          frame_capture_hls_settings:
                            description:
                              - Frame Capture Hls Settings
                            type: dict
                          standard_hls_settings:
                            description:
                              - Standard Hls Settings
                            type: dict
                            suboptions:
                              audio_rendition_sets:
                                description:
                                  - List all the audio groups that are used with the video output stream. Input all the audio GROUP-IDs that are associated to the video, separate by ','.
                                type: str
                              m3u8_settings:
                                description:
                                  - M3u8 Settings
                                type: dict
                                suboptions:
                                  audio_frames_per_pes:
                                    description:
                                      - The number of audio frames to insert for each PES packet.
                                    type: int
                                  audio_pids:
                                    description:
                                      - Packet Identifier (PID) of the elementary audio stream(s) in the transport stream. Multiple values are accepted, and can be entered in ranges and/or by comma separation. Can be entered as decimal or hexadecimal values. Each PID specified must be in the range of 32 (or 0x20)..8182 (or 0x1ff6).
                                    type: str
                                  ecm_pid:
                                    description:
                                      - This field is unused and deprecated.
                                    type: str
                                  nielsen_id3_behavior:
                                    description:
                                      - If set to PASSTHROUGH, Nielsen inaudible tones for media tracking will be detected in the input audio and an equivalent ID3 tag will be inserted in the output.
                                    type: str
                                    choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                                  pat_interval:
                                    description:
                                      - The number of milliseconds between instances of this table in the output transport stream. A value of "0" writes out the PMT once per segment file.
                                    type: int
                                  pcr_control:
                                    description:
                                      - When set to PCR_EVERY_PES_PACKET, a Program Clock Reference value is inserted for every Packetized Elementary Stream (PES) header. This parameter is effective only when the PCR PID is the same as the video or audio elementary stream.
                                    type: str
                                    choices: ['CONFIGURED_PCR_PERIOD', 'PCR_EVERY_PES_PACKET']
                                  pcr_period:
                                    description:
                                      - Maximum time in milliseconds between Program Clock References (PCRs) inserted into the transport stream.
                                    type: int
                                  pcr_pid:
                                    description:
                                      - Packet Identifier (PID) of the Program Clock Reference (PCR) in the transport stream. When no value is given, the encoder will assign the same value as the Video PID. Can be entered as a decimal or hexadecimal value.
                                    type: str
                                  pmt_interval:
                                    description:
                                      - The number of milliseconds between instances of this table in the output transport stream. A value of "0" writes out the PMT once per segment file.
                                    type: int
                                  pmt_pid:
                                    description:
                                      - Packet Identifier (PID) for the Program Map Table (PMT) in the transport stream. Can be entered as a decimal or hexadecimal value.
                                    type: str
                                  program_num:
                                    description:
                                      - The value of the program number field in the Program Map Table.
                                    type: int
                                  scte35_behavior:
                                    description:
                                      - If set to PASSTHROUGH, passes any SCTE-35 signals from the input source to this output.
                                    type: str
                                    choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                                  scte35_pid:
                                    description:
                                      - Packet Identifier (PID) of the SCTE-35 stream in the transport stream. Can be entered as a decimal or hexadecimal value.
                                    type: str
                                  timed_metadata_behavior:
                                    description:
                                      - Set to PASSTHROUGH to enable ID3 metadata insertion. To include metadata, you configure other parameters in the output group or individual outputs, or you add an ID3 action to the channel schedule.
                                    type: str
                                    choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                                  timed_metadata_pid:
                                    description:
                                      - Packet Identifier (PID) of the timed metadata stream in the transport stream. Can be entered as a decimal or hexadecimal value. Valid values are 32 (or 0x20)..8182 (or 0x1ff6).
                                    type: str
                                  transport_stream_id:
                                    description:
                                      - The value of the transport stream ID field in the Program Map Table.
                                    type: int
                                  video_pid:
                                    description:
                                      - Packet Identifier (PID) of the elementary video stream in the transport stream. Can be entered as a decimal or hexadecimal value.
                                    type: str
                                  klv_behavior:
                                    description:
                                      - If set to PASSTHROUGH, passes any KLV data from the input source to this output.
                                    type: str
                                    choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                                  klv_data_pids:
                                    description:
                                      - Packet Identifier (PID) for input source KLV data to this output. Multiple values are accepted, and can be entered in ranges and/or by comma separation. Can be entered as decimal or hexadecimal values. Each PID specified must be in the range of 32 (or 0x20)..8182 (or 0x1ff6).
                                    type: str
                      name_modifier:
                        description:
                          - String concatenated to the end of the destination filename. Accepts "Format Identifiers".
                        type: str
                      segment_modifier:
                        description:
                          - String concatenated to end of segment filenames.
                        type: str
                  media_package_output_settings:
                    description:
                      - Media Package Output Settings
                    type: dict
                  ms_smooth_output_settings:
                    description:
                      - Ms Smooth Output Settings
                    type: dict
                    suboptions:
                      h265_packaging_type:
                        description:
                          - Only applicable when this output is referencing an H.265 video description. Specifies whether MP4 segments should be packaged as HEV1 or HVC1.
                        type: str
                        choices: ['HEV1', 'HVC1']
                      name_modifier:
                        description:
                          - String concatenated to the end of the destination filename. Required for multiple outputs of the same type.
                        type: str
                  multiplex_output_settings:
                    description:
                      - Multiplex Output Settings
                    type: dict
                    suboptions:
                      destination:
                        description:
                          - Destination is a Multiplex.
                        type: dict
                        suboptions:
                          destination_ref_id:
                            description:
                              - Placeholder documentation for __string
                            type: str
                      container_settings:
                        description:
                          - Multiplex Container Settings
                        type: dict
                        suboptions:
                          multiplex_m2ts_settings:
                            description:
                              - Multiplex M2ts Settings
                            type: dict
                            suboptions:
                          
                              absent_input_audio_behavior:
                                description:
                                  - When set to DROP, output audio streams will be removed from the program if the selected input audio stream is removed from the input. This allows the output audio configuration to dynamically change based on input configuration. If this is set to ENCODE_SILENCE, all output audio streams will output encoded silence when not connected to an active input stream.
                                type: str
                                choices: ['DROP', 'ENCODE_SILENCE']
                              arib:
                                description:
                                  - When set to ENABLED, uses ARIB-compliant field muxing and removes video descriptor.
                                type: str
                                choices: ['DISABLED', 'ENABLED']
                              audio_buffer_model:
                                description:
                                  - When set to DVB, uses DVB buffer model for Dolby Digital audio. When set to ATSC, the ATSC model is used.
                                type: str
                                choices: ['ATSC', 'DVB']
                              audio_frames_per_pes:
                                description:
                                  - The number of audio frames to insert for each PES packet.
                                type: int
                              audio_stream_type:
                                description:
                                  - When set to ATSC, uses stream type = 0x81 for AC3 and stream type = 0x87 for EAC3. When set to DVB, uses stream type = 0x06.
                                type: str
                                choices: ['ATSC', 'DVB']
                              cc_descriptor:
                                description:
                                  - When set to ENABLED, generates captionServiceDescriptor in PMT.
                                type: str
                                choices: ['DISABLED', 'ENABLED']
                              ebif:
                                description:
                                  - If set to PASSTHROUGH, passes any EBIF data from the input source to this output.
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              es_rate_in_pes:
                                description:
                                  - Include or exclude the ES Rate field in the PES header.
                                type: str
                                choices: ['EXCLUDE', 'INCLUDE']
                              klv:
                                description:
                                  - If set to PASSTHROUGH, passes any KLV data from the input source to this output.
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              nielsen_id3_behavior:
                                description:
                                  - If set to PASSTHROUGH, Nielsen inaudible tones for media tracking will be detected in the input audio and an equivalent ID3 tag will be inserted in the output.
                                type: str
                                choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                              pcr_control:
                                description:
                                  - When set to PCR_EVERY_PES_PACKET, a Program Clock Reference value is inserted for every Packetized Elementary Stream (PES) header. This parameter is effective only when the PCR PID is the same as the video or audio elementary stream.
                                type: str
                                choices: ['CONFIGURED_PCR_PERIOD', 'PCR_EVERY_PES_PACKET']
                              pcr_period:
                                description:
                                  - Maximum time in milliseconds between Program Clock Reference (PCRs) inserted into the transport stream.
                                type: int
                              scte35_control:
                                description:
                                  - Optionally pass SCTE-35 signals from the input source to this output.
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              scte35_preroll_pullup_milliseconds:
                                description:
                                  - Defines the amount SCTE-35 preroll will be increased (in milliseconds) on the output. Preroll is the amount of time between the presence of a SCTE-35 indication in a transport stream and the PTS of the video frame it references. Zero means don't add pullup (it doesn't mean set the preroll to zero). Negative pullup is not supported, which means that you can't make the preroll shorter. Be aware that latency in the output will increase by the pullup amount.
                                type: float
                  rtmp_output_settings:
                    description:
                      - Rtmp Output Settings
                    type: dict
                    suboptions:
                      certificate_mode:
                        description:
                          - If set to VERIFY_AUTHENTICITY, verify the tls certificate chain to a trusted Certificate Authority (CA). This will cause rtmps outputs with self-signed certificates to fail.
                        type: str
                        choices: ['SELF_SIGNED', 'VERIFY_AUTHENTICITY']
                      connection_retry_interval:
                        description:
                          - Number of seconds to wait before retrying a connection to the Flash Media server if the connection is lost.
                        type: int
                      destination:
                        description:
                          - The RTMP endpoint excluding the stream name (eg. rtmp://host/appname). For connection to Akamai, a username and password must be supplied. URI fields accept format identifiers.
                        type: dict
                        suboptions:
                          destination_ref_id:
                            description:
                              - Placeholder documentation for __string
                            type: str
                      num_retries:
                        description:
                          - Number of retry attempts.
                        type: int
                  udp_output_settings:
                    description:
                      - Udp Output Settings
                    type: dict
                    suboptions:
                      buffer_msec:
                        description:
                          - UDP output buffering in milliseconds. Larger values increase latency through the transcoder but simultaneously assist the transcoder in maintaining a constant, low-jitter UDP/RTP output while accommodating clock recovery, input switching, input disruptions, picture reordering, etc.
                        type: int
                      container_settings:
                        description:
                          - Udp Container Settings
                        type: dict
                        suboptions:
                          m2ts_settings:
                            description:
                              - M2ts Settings
                            type: dict
                            suboptions:
                              absent_input_audio_behavior:
                                description:
                                  - When set to DROP, output audio streams will be removed from the program if the selected input audio stream is removed from the input. This allows the output audio configuration to dynamically change based on input configuration. If this is set to ENCODE_SILENCE, all output audio streams will output encoded silence when not connected to an active input stream.
                                type: str
                                choices: ['DROP', 'ENCODE_SILENCE']
                              arib:
                                description:
                                  - TODO
                                type: str
                                choices: ['DISABLED', 'ENABLED']
                              arib_captions_pid:
                                description:
                                  - TODO
                                type: str
                              arib_captions_pid_control:
                                description:
                                  - TODO
                                type: str
                                choices: ['AUTO', 'USE_CONFIGURED']
                              audio_buffer_model:
                                description:
                                  - TODO
                                type: str
                                choices: ['ATSC', 'DVB']
                              audio_frames_per_pes:
                                description:
                                  - TODO
                                type: int
                                      
                              audio_pids:
                                description:
                                  - TODO
                                type: str
                              audio_stream_type:
                                description:
                                  - TODO
                                type: str
                                choices: ['ATSC', 'DVB']
                              bitrate:
                                description:
                                  - TODO
                                type: int
                              buffer_model:
                                description:
                                  - TODO
                                type: str
                                choices: ['MULTIPLEX', 'NONE']
                              cc_descriptor:
                                description:
                                  - TODO
                                type: str
                                choices: ['DISABLED', 'ENABLED']
                              dvb_nit_settings:
                                description:
                                  - TODO
                                type: dict
                                suboptions:
                                  network_id:
                                    description:
                                      - TODO
                                    type: int
                                  network_name:
                                    description:
                                      - TODO
                                    type: str
                                  rep_interval:
                                    description:
                                      - TODO
                                    type: int
                              dvb_sdt_settings:
                                description:
                                  - TODO
                                type: dict
                                suboptions:
                                  output_sdt:
                                    description:
                                      - TODO
                                    type: str
                                    choices: ['SDT_FOLLOW', 'SDT_FOLLOW_IF_PRESENT', 'SDT_MANUAL', 'SDT_NONE']
                                  rep_interval:
                                    description:
                                      - TODO
                                    type: int
                                  service_name:
                                    description:
                                      - TODO
                                    type: str
                                  service_provider_name:
                                    description:
                                      - TODO
                                    type: str
                              dvb_sub_pids:
                                description:
                                  - TODO
                                type: str
                              dvb_tdt_settings:
                                description:
                                  - TODO
                                type: dict
                                suboptions:
                                  rep_interval:
                                    description:
                                      - TODO
                                    type: int
                              dvb_teletext_pid:
                                description:
                                  - TODO
                                type: str
                              ebif:
                                description:
                                  - TODO
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              ebp_audio_interval:
                                description:
                                  - TODO
                                type: str
                                choices: ['VIDEO_AND_FIXED_INTERVALS', 'VIDEO_INTERVAL']
                              ebp_lookahead_ms:
                                description:
                                  - TODO
                                type: int
                              ebp_placement:
                                description:
                                  - TODO
                                type: str
                                choices: ['VIDEO_AND_AUDIO_PIDS', 'VIDEO_PID']
                              ecm_pid:
                                description:
                                  - TODO
                                type: str
                              es_rate_in_pes:
                                description:
                                  - TODO
                                type: str
                                choices: ['EXCLUDE', 'INCLUDE']
                              etv_platform_pid:
                                description:
                                  - TODO
                                type: str
                              etv_signal_pid:
                                description:
                                  - TODO
                                type: str
                              fragment_time:
                                description:
                                  - TODO
                                type: float
                              klv:
                                description:
                                  - TODO
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              klv_data_pids:
                                description:
                                  - TODO
                                type: str
                              nielsen_id3_behavior:
                                description:
                                  - TODO
                                type: str
                                choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                              null_packet_bitrate:
                                description:
                                  - TODO
                                type: float
                              pat_interval:
                                description:
                                  - TODO
                                type: int
                              pcr_control:
                                description:
                                  - TODO
                                type: str
                                choices: ['CONFIGURED_PCR_PERIOD', 'PCR_EVERY_PES_PACKET']
                              pcr_period:
                                description:
                                  - TODO
                                type: int
                              pcr_pid:
                                description:
                                  - TODO
                                type: str
                              pmt_interval:
                                description:
                                  - TODO
                                type: int
                              pmt_pid:
                                description:
                                  - TODO
                                type: str
                              program_num:
                                description:
                                  - TODO
                                type: int
                              rate_mode:
                                description:
                                  - TODO
                                type: str
                                choices: ['CBR', 'VBR']
                              scte27_pids:
                                description:
                                  - TODO
                                type: str
                              scte35_control:
                                description:
                                  - TODO
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              scte35_pid:
                                description:
                                  - TODO
                                type: str
                              segmentation_markers:
                                description:
                                  - TODO
                                type: str
                                choices: ['EBP', 'EBP_LEGACY', 'NONE', 'PSI_SEGSTART', 'RAI_ADAPT', 'RAI_SEGSTART']
                              segmentation_style:
                                description:
                                  - TODO
                                type: str
                                choices: ['MAINTAIN_CADENCE', 'RESET_CADENCE']
                              segmentation_time:
                                description:
                                  - TODO
                                type: float
                              timed_metadata_behavior:
                                description:
                                  - TODO
                                type: str
                                choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                              timed_metadata_pid:
                                description:
                                  - TODO
                                type: str
                              transport_stream_id:
                                description:
                                  - TODO
                                type: int
                              video_pid:
                                description:
                                  - TODO
                                type: str
                              scte35_preroll_pullup_milliseconds:
                                description:
                                  - TODO
                                type: float
                      destination:
                        description:
                          - Destination address and port number for RTP or UDP packets. Can be unicast or multicast RTP or UDP (eg. rtp://239.10.10.10:5001 or udp://10.100.100.100:5002).
                        type: dict
                        suboptions:
                          destination_ref_id:
                            description:
                              - Placeholder documentation for __string
                            type: str
                      fec_output_settings:
                        description:
                          - Settings for enabling and adjusting Forward Error Correction on UDP outputs.
                        type: dict
                        suboptions:
                          column_depth:
                            description:
                              - Parameter D from SMPTE 2022-1. The height of the FEC protection matrix. The number of transport stream packets per column error correction packet. Must be between 4 and 20, inclusive.
                            type: int
                          include_fec:
                            description:
                              - Enables column only or column and row based FEC
                            type: str
                            choices: ['COLUMN', 'COLUMN_AND_ROW']
                          row_length:
                            description:
                              - Parameter L from SMPTE 2022-1. The width of the FEC protection matrix. Must be between 1 and 20, inclusive. If only Column FEC is used, then larger values increase robustness. If Row FEC is used, then this is the number of transport stream packets per row error correction packet, and the value must be between 4 and 20, inclusive, if includeFec is COLUMN_AND_ROW. If includeFec is COLUMN, this value must be 1 to 20, inclusive.
                            type: int
                  cmaf_ingest_output_settings:
                    description:
                      - Cmaf Ingest Output Settings
                    type: dict
                    suboptions:
                      name_modifier:
                        description:
                          - String concatenated to the end of the destination filename. Required for multiple outputs of the same type.
                        type: str
                  srt_output_settings:
                    description:
                      - Srt Output Settings
                    type: dict
                    suboptions:
                      buffer_msec:
                        description:
                          - SRT output buffering in milliseconds. A higher value increases latency through the encoder. But the benefits are that it helps to maintain a constant, low-jitter SRT output, and it accommodates clock recovery, input switching, input disruptions, picture reordering, and so on. Range, 0-10000 milliseconds.
                        type: int
                      container_settings:
                        description:
                          - Udp Container Settings
                        type: dict
                        suboptions:
                          m2ts_settings:
                            description:
                              - M2ts Settings
                            type: dict
                            suboptions:
                              absent_input_audio_behavior:
                                description:
                                  - When set to DROP, output audio streams will be removed from the program if the selected input audio stream is removed from the input. This allows the output audio configuration to dynamically change based on input configuration. If this is set to ENCODE_SILENCE, all output audio streams will output encoded silence when not connected to an active input stream.
                                type: str
                                choices: ['DROP', 'ENCODE_SILENCE']
                              arib:
                                description:
                                  - TODO
                                type: str
                                choices: ['DISABLED', 'ENABLED']
                              arib_captions_pid:
                                description:
                                  - TODO
                                type: str
                              arib_captions_pid_control:
                                description:
                                  - TODO
                                type: str
                                choices: ['AUTO', 'USE_CONFIGURED']
                              audio_buffer_model:
                                description:
                                  - TODO
                                type: str
                                choices: ['ATSC', 'DVB']
                              audio_frames_per_pes:
                                description:
                                  - TODO
                                type: int
                                      
                              audio_pids:
                                description:
                                  - TODO
                                type: str
                              audio_stream_type:
                                description:
                                  - TODO
                                type: str
                                choices: ['ATSC', 'DVB']
                              bitrate:
                                description:
                                  - TODO
                                type: int
                              buffer_model:
                                description:
                                  - TODO
                                type: str
                                choices: ['MULTIPLEX', 'NONE']
                              cc_descriptor:
                                description:
                                  - TODO
                                type: str
                                choices: ['DISABLED', 'ENABLED']
                              dvb_nit_settings:
                                description:
                                  - TODO
                                type: dict
                                suboptions:
                                  network_id:
                                    description:
                                      - TODO
                                    type: int
                                  network_name:
                                    description:
                                      - TODO
                                    type: str
                                  rep_interval:
                                    description:
                                      - TODO
                                    type: int
                              dvb_sdt_settings:
                                description:
                                  - TODO
                                type: dict
                                suboptions:
                                  output_sdt:
                                    description:
                                      - TODO
                                    type: str
                                    choices: ['SDT_FOLLOW', 'SDT_FOLLOW_IF_PRESENT', 'SDT_MANUAL', 'SDT_NONE']
                                  rep_interval:
                                    description:
                                      - TODO
                                    type: int
                                  service_name:
                                    description:
                                      - TODO
                                    type: str
                                  service_provider_name:
                                    description:
                                      - TODO
                                    type: str
                              dvb_sub_pids:
                                description:
                                  - TODO
                                type: str
                              dvb_tdt_settings:
                                description:
                                  - TODO
                                type: dict
                                suboptions:
                                  rep_interval:
                                    description:
                                      - TODO
                                    type: int
                              dvb_teletext_pid:
                                description:
                                  - TODO
                                type: str
                              ebif:
                                description:
                                  - TODO
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              ebp_audio_interval:
                                description:
                                  - TODO
                                type: str
                                choices: ['VIDEO_AND_FIXED_INTERVALS', 'VIDEO_INTERVAL']
                              ebp_lookahead_ms:
                                description:
                                  - TODO
                                type: int
                              ebp_placement:
                                description:
                                  - TODO
                                type: str
                                choices: ['VIDEO_AND_AUDIO_PIDS', 'VIDEO_PID']
                              ecm_pid:
                                description:
                                  - TODO
                                type: str
                              es_rate_in_pes:
                                description:
                                  - TODO
                                type: str
                                choices: ['EXCLUDE', 'INCLUDE']
                              etv_platform_pid:
                                description:
                                  - TODO
                                type: str
                              etv_signal_pid:
                                description:
                                  - TODO
                                type: str
                              fragment_time:
                                description:
                                  - TODO
                                type: float
                              klv:
                                description:
                                  - TODO
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              klv_data_pids:
                                description:
                                  - TODO
                                type: str
                              nielsen_id3_behavior:
                                description:
                                  - TODO
                                type: str
                                choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                              null_packet_bitrate:
                                description:
                                  - TODO
                                type: float
                              pat_interval:
                                description:
                                  - TODO
                                type: int
                              pcr_control:
                                description:
                                  - TODO
                                type: str
                                choices: ['CONFIGURED_PCR_PERIOD', 'PCR_EVERY_PES_PACKET']
                              pcr_period:
                                description:
                                  - TODO
                                type: int
                              pcr_pid:
                                description:
                                  - TODO
                                type: str
                              pmt_interval:
                                description:
                                  - TODO
                                type: int
                              pmt_pid:
                                description:
                                  - TODO
                                type: str
                              program_num:
                                description:
                                  - TODO
                                type: int
                              rate_mode:
                                description:
                                  - TODO
                                type: str
                                choices: ['CBR', 'VBR']
                              scte27_pids:
                                description:
                                  - TODO
                                type: str
                              scte35_control:
                                description:
                                  - TODO
                                type: str
                                choices: ['NONE', 'PASSTHROUGH']
                              scte35_pid:
                                description:
                                  - TODO
                                type: str
                              segmentation_markers:
                                description:
                                  - TODO
                                type: str
                                choices: ['EBP', 'EBP_LEGACY', 'NONE', 'PSI_SEGSTART', 'RAI_ADAPT', 'RAI_SEGSTART']
                              segmentation_style:
                                description:
                                  - TODO
                                type: str
                                choices: ['MAINTAIN_CADENCE', 'RESET_CADENCE']
                              segmentation_time:
                                description:
                                  - TODO
                                type: float
                              timed_metadata_behavior:
                                description:
                                  - TODO
                                type: str
                                choices: ['NO_PASSTHROUGH', 'PASSTHROUGH']
                              timed_metadata_pid:
                                description:
                                  - TODO
                                type: str
                              transport_stream_id:
                                description:
                                  - TODO
                                type: int
                              video_pid:
                                description:
                                  - TODO
                                type: str
                              scte35_preroll_pullup_milliseconds:
                                description:
                                  - TODO
                                type: float
                      destination:
                        description:
                          - Reference to an OutputDestination ID defined in the channel
                        type: dict
                        suboptions:
                          destination_ref_id:
                            description:
                              - Placeholder documentation for __string
                            type: str
                      encryption_type:
                        description:
                          - The encryption level for the content. Valid values are AES128, AES192, AES256. You and the downstream system should plan how to set this field because the values must not conflict with each other.
                        type: str
                        choices: ['AES128', 'AES192', 'AES256']
                      latency:
                        description:
                          - The latency value, in milliseconds, that is proposed during the SRT connection handshake. SRT will choose the maximum of the values proposed by the sender and receiver. On the sender side, latency is the amount of time a packet is held to give it a chance to be delivered successfully. On the receiver side, latency is the amount of time the packet is held before delivering to the application, aiding in packet recovery and matching as closely as possible the packet timing of the sender. Range, 40-16000 milliseconds.
                        type: int
              video_description_name:
                description:
                  - The name of the VideoDescription used as the source for this output.
                type: str
      timecode_config:
        description:
          - Contains settings used to acquire and adjust timecode information from inputs.
        type: dict
        suboptions:
          source:
            description:
              - Identifies the source for the timecode that will be associated with the events outputs. -EMBEDDED (embedded) Initialize the output timecode with timecode from the the source. If no embedded timecode is detected in the source, the system falls back to using "Start at 0" (zerobased). -System Clock (systemclock) Use the UTC time. -Start at 0 (zerobased) The time of the first frame of the event will be 00:00:00:00.
            type: str
            choices: ['EMBEDDED', 'SYSTEMCLOCK', 'ZEROBASED']
          sync_threshold:
            description:
              - Threshold in frames beyond which output timecode is resynchronized to the input timecode. Discrepancies below this threshold are permitted to avoid unnecessary discontinuities in the output timecode. No timecode sync when this is not specified.
            type: int
      video_descriptions:
        description:
          - Video settings for this stream.
        type: list
        elements: dict
        suboptions:
          codec_settings:
            description:
              - Video codec settings.
            type: dict
            suboptions:
              frame_capture_settings:
                description:
                  - Frame Capture Settings
                type: dict
                suboptions:
                  capture_interval:
                    description:
                      - The frequency at which to capture frames for inclusion in the output. May be specified in either seconds or milliseconds, as specified by captureIntervalUnits.
                    type: int
                  capture_interval_units:
                    description:
                      - Unit for the frame capture interval.
                    type: str
                    choices: ['MILLISECONDS', 'SECONDS']
                  timecode_burnin_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      font_size:
                        description:
                          - TODO
                        type: str
                        choices: ['EXTRA_SMALL_10', 'LARGE_48', 'MEDIUM_32', 'SMALL_16']
                      position:
                        description:
                          - TODO
                        type: str
                        choices:
                          - 'BOTTOM_CENTER'
                          - 'BOTTOM_LEFT'
                          - 'BOTTOM_RIGHT'
                          - 'MIDDLE_CENTER'
                          - 'MIDDLE_LEFT'
                          - 'MIDDLE_RIGHT'
                          - 'TOP_CENTER'
                          - 'TOP_LEFT'
                          - 'TOP_RIGHT'
                      prefix:
                        description:
                          - TODO
                        type: str
              h264_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  adaptive_quantization:
                    description:
                      - TODO
                    type: str
                    choices: ['AUTO', 'HIGH', 'HIGHER', 'LOW', 'MAX', 'MEDIUM', 'OFF']
                  afd_signaling:
                    description:
                      - TODO
                    type: str
                    choices: ['AUTO', 'FIXED', 'NONE']
                  bitrate:
                    description:
                      - TODO
                    type: int
                  buf_fill_pct:
                    description:
                      - TODO
                    type: int
                  buf_size:
                    description:
                      - TODO
                    type: int
                  color_metadata:
                    description:
                      - TODO
                    type: str
                    choices: ['IGNORE', 'INSERT']
                  color_space_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      color_space_passthrough_settings:
                        description:
                          - TODO
                        type: dict
                      rec601_settings:
                        description:
                          - TODO
                        type: dict
                      rec709_settings:
                        description:
                          - TODO
                        type: dict
                  entropy_encoding:
                    description:
                      - TODO
                    type: str
                    choices: ['CABAC', 'CAVLC']
                  filter_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      temporal_filter_settings:
                        description:
                          - TODO
                        type: dict
                        suboptions:
                          post_filter_sharpening:
                            description:
                              - TODO
                            type: str
                            choices: ['AUTO', 'DISABLED', 'ENABLED']
                          strength:
                            description:
                              - TODO
                            type: str
                            choices:
                              - 'AUTO'
                              - 'STRENGTH_1'
                              - 'STRENGTH_2'
                              - 'STRENGTH_3'
                              - 'STRENGTH_4'
                              - 'STRENGTH_5'
                              - 'STRENGTH_6'
                              - 'STRENGTH_7'
                              - 'STRENGTH_8'
                              - 'STRENGTH_9'
                              - 'STRENGTH_10'
                              - 'STRENGTH_11'
                              - 'STRENGTH_12'
                              - 'STRENGTH_13'
                              - 'STRENGTH_14'
                              - 'STRENGTH_15'
                              - 'STRENGTH_16'
                      bandwidth_reduction_filter_settings:
                        description:
                          - TODO
                        type: dict
                        suboptions:
                          post_filter_sharpening:
                            description:
                              - TODO
                            type: str
                            choices: ['DISABLED', 'SHARPENING_1', 'SHARPENING_2', 'SHARPENING_3']
                          strength:
                            description:
                              - TODO
                            type: str
                            choices: ['AUTO', 'STRENGTH_1', 'STRENGTH_2', 'STRENGTH_3', 'STRENGTH_4']
                  fixed_afd:
                    description:
                      - TODO
                    type: str
                    choices:
                      - 'AFD_0000'
                      - 'AFD_0010'
                      - 'AFD_0011'
                      - 'AFD_0100'
                      - 'AFD_1000'
                      - 'AFD_1001'
                      - 'AFD_1010'
                      - 'AFD_1011'
                      - 'AFD_1101'
                      - 'AFD_1110'
                      - 'AFD_1111'
                  flicker_aq:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  force_field_pictures:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  framerate_control:
                    description:
                      - TODO
                    type: str
                    choices: ['INITIALIZE_FROM_SOURCE', 'SPECIFIED']
                  framerate_denominator:
                    description:
                      - TODO
                    type: int
                  framerate_numerator:
                    description:
                      - TODO
                    type: int
                  gop_b_reference:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  gop_closed_cadence:
                    description:
                      - TODO
                    type: int
                  gop_num_b_frames:
                    description:
                      - TODO
                    type: int
                  gop_size:
                    description:
                      - TODO
                    type: float
                      
                  gop_size_units:
                    description:
                      - TODO
                    type: str
                    choices: ['FRAMES', 'SECONDS']
                  level:
                    description:
                      - TODO
                    type: str
                    choices:
                      - 'H264_LEVEL_1'
                      - 'H264_LEVEL_1_1'
                      - 'H264_LEVEL_1_2'
                      - 'H264_LEVEL_1_3'
                      - 'H264_LEVEL_2'
                      - 'H264_LEVEL_2_1'
                      - 'H264_LEVEL_2_2'
                      - 'H264_LEVEL_3'
                      - 'H264_LEVEL_3_1'
                      - 'H264_LEVEL_3_2'
                      - 'H264_LEVEL_4'
                      - 'H264_LEVEL_4_1'
                      - 'H264_LEVEL_4_2'
                      - 'H264_LEVEL_5'
                      - 'H264_LEVEL_5_1'
                      - 'H264_LEVEL_5_2'
                      - 'H264_LEVEL_AUTO'
                  look_ahead_rate_control:
                    description:
                      - TODO
                    type: str
                    choices: ['HIGH', 'LOW', 'MEDIUM']
                  max_bitrate:
                    description:
                      - TODO
                    type: int
                  min_i_interval:
                    description:
                      - TODO
                    type: int
                  num_ref_frames:
                    description:
                      - TODO
                    type: int
                  par_control:
                    description:
                      - TODO
                    type: str
                    choices: ['INITIALIZE_FROM_SOURCE', 'SPECIFIED']
                  par_denominator:
                    description:
                      - TODO
                    type: int
                  par_numerator:
                    description:
                      - TODO
                    type: int
                  profile:
                    description:
                      - TODO
                    type: str
                    choices: ['BASELINE', 'HIGH', 'HIGH_10BIT', 'HIGH_422', 'HIGH_422_10BIT', 'MAIN']
                  quality_level:
                    description:
                      - TODO
                    type: str
                    choices: ['ENHANCED_QUALITY', 'STANDARD_QUALITY']
                  qvbr_quality_level:
                    description:
                      - TODO
                    type: int
                  rate_control_mode:
                    description:
                      - TODO
                    type: str
                    choices: ['CBR', 'MULTIPLEX', 'QVBR', 'VBR']
                  scan_type:
                    description:
                      - TODO
                    type: str
                    choices: ['INTERLACED', 'PROGRESSIVE']
                  scene_change_detect:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  slices:
                    description:
                      - TODO
                    type: int
                  softness:
                    description:
                      - TODO
                    type: int
                  spatial_aq:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  subgop_length:
                    description:
                      - TODO
                    type: str
                    choices: ['DYNAMIC', 'FIXED']
                  syntax:
                    description:
                      - TODO
                    type: str
                    choices: ['DEFAULT', 'RP2027']
                  temporal_aq:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  timecode_insertion:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'PIC_TIMING_SEI']
                  timecode_burnin_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      font_size:
                        description:
                          - TODO
                        type: str
                        choices: ['EXTRA_SMALL_10', 'LARGE_48', 'MEDIUM_32', 'SMALL_16']
                      position:
                        description:
                          - TODO
                        type: str
                        choices:
                          - 'BOTTOM_CENTER'
                          - 'BOTTOM_LEFT'
                          - 'BOTTOM_RIGHT'
                          - 'MIDDLE_CENTER'
                          - 'MIDDLE_LEFT'
                          - 'MIDDLE_RIGHT'
                          - 'TOP_CENTER'
                          - 'TOP_LEFT'
                          - 'TOP_RIGHT'
                      prefix:
                        description:
                          - TODO
                        type: str
                  min_qp:
                    description:
                      - TODO
                    type: int
              h265_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  adaptive_quantization:
                    description:
                      - TODO
                    type: str
                    choices: ['AUTO', 'HIGH', 'HIGHER', 'LOW', 'MAX', 'MEDIUM', 'OFF']
                  afd_signaling:
                    description:
                      - TODO
                    type: str
                    choices: ['AUTO', 'FIXED', 'NONE']
                  alternative_transfer_function:
                    description:
                      - TODO
                    type: str
                    choices: ['INSERT', 'OMIT']
                  bitrate:
                    description:
                      - TODO
                    type: int
                  buf_size:
                    description:
                      - TODO
                    type: int
                  color_metadata:
                    description:
                      - TODO
                    type: str
                    choices: ['IGNORE', 'INSERT']
                  color_space_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      color_space_passthrough_settings:
                        description:
                          - TODO
                        type: dict
                      dolby_vision81_settings:
                        description:
                          - TODO
                        type: dict
                      hdr10_settings:
                        description:
                          - TODO
                        type: dict
                        suboptions:
                          max_cll:
                            description:
                              - TODO
                            type: int
                          max_fall:
                            description:
                              - TODO
                            type: int
                      rec601_settings:
                        description:
                          - TODO
                        type: dict
                      rec709_settings:
                        description:
                          - TODO
                        type: dict
                  filter_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      temporal_filter_settings:
                        description:
                          - TODO
                        type: dict
                        suboptions:
                          post_filter_sharpening:
                            description:
                              - TODO
                            type: str
                            choices: ['AUTO', 'DISABLED', 'ENABLED']
                          strength:
                            description:
                              - TODO
                            type: str
                            choices:
                              - 'AUTO'
                              - 'STRENGTH_1'
                              - 'STRENGTH_2'
                              - 'STRENGTH_3'
                              - 'STRENGTH_4'
                              - 'STRENGTH_5'
                              - 'STRENGTH_6'
                              - 'STRENGTH_7'
                              - 'STRENGTH_8'
                              - 'STRENGTH_9'
                              - 'STRENGTH_10'
                              - 'STRENGTH_11'
                              - 'STRENGTH_12'
                              - 'STRENGTH_13'
                              - 'STRENGTH_14'
                              - 'STRENGTH_15'
                              - 'STRENGTH_16'
                      bandwidth_reduction_filter_settings:
                        description:
                          - TODO
                        type: dict
                        suboptions:
                          post_filter_sharpening:
                            description:
                              - TODO
                            type: str
                            choices: ['DISABLED', 'SHARPENING_1', 'SHARPENING_2', 'SHARPENING_3']
                          strength:
                            description:
                              - TODO
                            type: str
                            choices: ['AUTO', 'STRENGTH_1', 'STRENGTH_2', 'STRENGTH_3', 'STRENGTH_4']
                  fixed_afd:
                    description:
                      - TODO
                    type: str
                    choices:
                      - 'AFD_0000'
                      - 'AFD_0010'
                      - 'AFD_0011'
                      - 'AFD_0100'
                      - 'AFD_1000'
                      - 'AFD_1001'
                      - 'AFD_1010'
                      - 'AFD_1011'
                      - 'AFD_1101'
                      - 'AFD_1110'
                      - 'AFD_1111'
                  flicker_aq:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  framerate_denominator:
                    description:
                      - TODO
                    type: int
                  framerate_numerator:
                    description:
                      - TODO
                    type: int
                  gop_closed_cadence:
                    description:
                      - TODO
                    type: int
                  gop_size:
                    description:
                      - TODO
                    type: float
                      
                  gop_size_units:
                    description:
                      - TODO
                    type: str
                    choices: ['FRAMES', 'SECONDS']
                  level:
                    description:
                      - TODO
                    type: str
                    choices:
                      - 'H265_LEVEL_1'
                      - 'H265_LEVEL_2'
                      - 'H265_LEVEL_2_1'
                      - 'H265_LEVEL_3'
                      - 'H265_LEVEL_3_1'
                      - 'H265_LEVEL_4'
                      - 'H265_LEVEL_4_1'
                      - 'H265_LEVEL_5'
                      - 'H265_LEVEL_5_1'
                      - 'H265_LEVEL_5_2'
                      - 'H265_LEVEL_6'
                      - 'H265_LEVEL_6_1'
                      - 'H265_LEVEL_6_2'
                      - 'H265_LEVEL_AUTO'
                  look_ahead_rate_control:
                    description:
                      - TODO
                    type: str
                    choices: ['HIGH', 'LOW', 'MEDIUM']
                  max_bitrate:
                    description:
                      - TODO
                    type: int
                  min_i_interval:
                    description:
                      - TODO
                    type: int
                  par_denominator:
                    description:
                      - TODO
                    type: int
                  par_numerator:
                    description:
                      - TODO
                    type: int
                  profile:
                    description:
                      - TODO
                    type: str
                    choices: ['MAIN', 'MAIN_10BIT']
                  qvbr_quality_level:
                    description:
                      - TODO
                    type: int
                  rate_control_mode:
                    description:
                      - TODO
                    type: str
                    choices: ['CBR', 'MULTIPLEX', 'QVBR']
                  scan_type:
                    description:
                      - TODO
                    type: str
                    choices: ['INTERLACED', 'PROGRESSIVE']
                  scene_change_detect:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  slices:
                    description:
                      - TODO
                    type: int
                  tier:
                    description:
                      - TODO
                    type: str
                    choices: ['HIGH', 'MAIN']
                  timecode_insertion:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'PIC_TIMING_SEI']
                  timecode_burnin_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      font_size:
                        description:
                          - TODO
                        type: str
                        choices: ['EXTRA_SMALL_10', 'LARGE_48', 'MEDIUM_32', 'SMALL_16']
                      position:
                        description:
                          - TODO
                        type: str
                        choices:
                          - 'BOTTOM_CENTER'
                          - 'BOTTOM_LEFT'
                          - 'BOTTOM_RIGHT'
                          - 'MIDDLE_CENTER'
                          - 'MIDDLE_LEFT'
                          - 'MIDDLE_RIGHT'
                          - 'TOP_CENTER'
                          - 'TOP_LEFT'
                          - 'TOP_RIGHT'
                      prefix:
                        description:
                          - TODO
                        type: str
                  mv_over_picture_boundaries:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  mv_temporal_predictor:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  tile_height:
                    description:
                      - TODO
                    type: int
                  tile_padding:
                    description:
                      - TODO
                    type: str
                    choices: ['NONE', 'PADDED']
                  tile_width:
                    description:
                      - TODO
                    type: int
                  treeblock_size:
                    description:
                      - TODO
                    type: str
                    choices: ['AUTO', 'TREE_SIZE_32X32']
                  min_qp:
                    description:
                      - TODO
                    type: int
                  deblocking:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
              mpeg2_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  adaptive_quantization:
                    description:
                      - TODO
                    type: str
                    choices: ['AUTO', 'HIGH', 'LOW', 'MEDIUM', 'OFF']
                  afd_signaling:
                    description:
                      - TODO
                    type: str
                    choices: ['AUTO', 'FIXED', 'NONE']
                  color_metadata:
                    description:
                      - TODO
                    type: str
                    choices: ['IGNORE', 'INSERT']
                  color_space:
                    description:
                      - TODO
                    type: str
                    choices: ['AUTO', 'PASSTHROUGH']
                  display_aspect_ratio:
                    description:
                      - TODO
                    type: str
                    choices: ['DISPLAYRATIO16X9', 'DISPLAYRATIO4X3']
                  filter_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      temporal_filter_settings:
                        description:
                          - TODO
                        type: dict
                        suboptions:
                          post_filter_sharpening:
                            description:
                              - TODO
                            type: str
                            choices: ['AUTO', 'DISABLED', 'ENABLED']
                          strength:
                            description:
                              - TODO
                            type: str
                            choices:
                              - 'AUTO'
                              - 'STRENGTH_1'
                              - 'STRENGTH_2'
                              - 'STRENGTH_3'
                              - 'STRENGTH_4'
                              - 'STRENGTH_5'
                              - 'STRENGTH_6'
                              - 'STRENGTH_7'
                              - 'STRENGTH_8'
                              - 'STRENGTH_9'
                              - 'STRENGTH_10'
                              - 'STRENGTH_11'
                              - 'STRENGTH_12'
                              - 'STRENGTH_13'
                              - 'STRENGTH_14'
                              - 'STRENGTH_15'
                              - 'STRENGTH_16'
                  fixed_afd:
                    description:
                      - TODO
                    type: str
                    choices:
                      - 'AFD_0000'
                      - 'AFD_0010'
                      - 'AFD_0011'
                      - 'AFD_0100'
                      - 'AFD_1000'
                      - 'AFD_1001'
                      - 'AFD_1010'
                      - 'AFD_1011'
                      - 'AFD_1101'
                      - 'AFD_1110'
                      - 'AFD_1111'
                  framerate_denominator:
                    description:
                      - TODO
                    type: int
                  framerate_numerator:
                    description:
                      - TODO
                    type: int
                  gop_closed_cadence:
                    description:
                      - TODO
                    type: int
                  gop_num_b_frames:
                    description:
                      - TODO
                    type: int
                  gop_size:
                    description:
                      - TODO
                    type: float
                      
                  gop_size_units:
                    description:
                      - TODO
                    type: str
                    choices: ['FRAMES', 'SECONDS']
                  scan_type:
                    description:
                      - TODO
                    type: str
                    choices: ['INTERLACED', 'PROGRESSIVE']
                  subgop_length:
                    description:
                      - TODO
                    type: str
                    choices: ['DYNAMIC', 'FIXED']
                  timecode_insertion:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'GOP_TIMECODE']
                  timecode_burnin_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      font_size:
                        description:
                          - TODO
                        type: str
                        choices: ['EXTRA_SMALL_10', 'LARGE_48', 'MEDIUM_32', 'SMALL_16']
                      position:
                        description:
                          - TODO
                        type: str
                        choices:
                          - 'BOTTOM_CENTER'
                          - 'BOTTOM_LEFT'
                          - 'BOTTOM_RIGHT'
                          - 'MIDDLE_CENTER'
                          - 'MIDDLE_LEFT'
                          - 'MIDDLE_RIGHT'
                          - 'TOP_CENTER'
                          - 'TOP_LEFT'
                          - 'TOP_RIGHT'
                      prefix:
                        description:
                          - TODO
                        type: str
              av1_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  afd_signaling:
                    description:
                      - TODO
                    type: str
                    choices: ['AUTO', 'FIXED', 'NONE']
                  buf_size:
                    description:
                      - TODO
                    type: int
                  color_space_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      color_space_passthrough_settings:
                        description:
                          - TODO
                        type: dict
                      hdr10_settings:
                        description:
                          - TODO
                        type: dict
                        suboptions:
                          
                          max_cll:
                            description:
                              - TODO
                            type: int
                            
                          max_fall:
                            description:
                              - TODO
                            type: int
                      rec601_settings:
                        description:
                          - TODO
                        type: dict
                      rec709_settings:
                        description:
                          - TODO
                        type: dict
                  fixed_afd:
                    description:
                      - TODO
                    type: str
                    choices:
                      - 'AFD_0000'
                      - 'AFD_0010'
                      - 'AFD_0011'
                      - 'AFD_0100'
                      - 'AFD_1000'
                      - 'AFD_1001'
                      - 'AFD_1010'
                      - 'AFD_1011'
                      - 'AFD_1101'
                      - 'AFD_1110'
                      - 'AFD_1111'
                  framerate_denominator:
                    description:
                      - TODO
                    type: int
                  framerate_numerator:
                    description:
                      - TODO
                    type: int
                  gop_size:
                    description:
                      - TODO
                    type: float
                      
                  gop_size_units:
                    description:
                      - TODO
                    type: str
                    choices: ['FRAMES', 'SECONDS']
                  level:
                    description:
                      - TODO
                    type: str
                    choices:
                      - 'AV1_LEVEL_2'
                      - 'AV1_LEVEL_2_1'
                      - 'AV1_LEVEL_3'
                      - 'AV1_LEVEL_3_1'
                      - 'AV1_LEVEL_4'
                      - 'AV1_LEVEL_4_1'
                      - 'AV1_LEVEL_5'
                      - 'AV1_LEVEL_5_1'
                      - 'AV1_LEVEL_5_2'
                      - 'AV1_LEVEL_5_3'
                      - 'AV1_LEVEL_6'
                      - 'AV1_LEVEL_6_1'
                      - 'AV1_LEVEL_6_2'
                      - 'AV1_LEVEL_6_3'
                      - 'AV1_LEVEL_AUTO'
                  look_ahead_rate_control:
                    description:
                      - TODO
                    type: str
                    choices: ['HIGH', 'LOW', 'MEDIUM']
                  max_bitrate:
                    description:
                      - TODO
                    type: int
                  min_i_interval:
                    description:
                      - TODO
                    type: int
                  par_denominator:
                    description:
                      - TODO
                    type: int
                  par_numerator:
                    description:
                      - TODO
                    type: int
                  qvbr_quality_level:
                    description:
                      - TODO
                    type: int
                  scene_change_detect:
                    description:
                      - TODO
                    type: str
                    choices: ['DISABLED', 'ENABLED']
                  timecode_burnin_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      font_size:
                        description:
                          - TODO
                        type: str
                        choices: ['EXTRA_SMALL_10', 'LARGE_48', 'MEDIUM_32', 'SMALL_16']
                      position:
                        description:
                          - TODO
                        type: str
                        choices:
                          - 'BOTTOM_CENTER'
                          - 'BOTTOM_LEFT'
                          - 'BOTTOM_RIGHT'
                          - 'MIDDLE_CENTER'
                          - 'MIDDLE_LEFT'
                          - 'MIDDLE_RIGHT'
                          - 'TOP_CENTER'
                          - 'TOP_LEFT'
                          - 'TOP_RIGHT'
                      prefix:
                        description:
                          - TODO
                        type: str
          height:
            description:
              - Output video height, in pixels. Must be an even number. For most codecs, you can leave this field and width blank in order to use the height and width (resolution) from the source. Note, however, that leaving blank is not recommended. For the Frame Capture codec, height and width are required.
            type: int
          name:
            description:
              - TODO
            type: str
          respond_to_afd:
            description:
              - Indicates how MediaLive will respond to the AFD values that might be in the input video. If you do not know what AFD signaling is, or if your downstream system has not given you guidance, choose PASSTHROUGH. RESPOND - MediaLive clips the input video using a formula that uses the AFD values (configured in afdSignaling ), the input display aspect ratio, and the output display aspect ratio. MediaLive also includes the AFD values in the output, unless the codec for this encode is FRAME_CAPTURE. PASSTHROUGH - MediaLive ignores the AFD values and does not clip the video. But MediaLive does include the values in the output. NONE - MediaLive does not clip the input video and does not include the AFD values in the output
            type: str
            choices: ['NONE', 'PASSTHROUGH', 'RESPOND']
          scaling_behavior:
            description:
              - STRETCH_TO_OUTPUT configures the output position to stretch the video to the specified output resolution (height and width). This option will override any position value. DEFAULT may insert black boxes (pillar boxes or letter boxes) around the video to provide the specified output resolution.
            type: str
            choices: ['DEFAULT', 'STRETCH_TO_OUTPUT']
          sharpness:
            description:
              - Changes the strength of the anti-alias filter used for scaling. 0 is the softest setting, 100 is the sharpest. A setting of 50 is recommended for most content.
            type: int
          width:
            description:
              - Output video width, in pixels. Must be an even number. For most codecs, you can leave this field and height blank in order to use the height and width (resolution) from the source. Note, however, that leaving blank is not recommended. For the Frame Capture codec, height and width are required.
            type: int
      thumbnail_configuration:
        description:
          - Thumbnail configuration settings.
        type: dict
        suboptions:
          state:
            description:
              - Enables the thumbnail feature. The feature generates thumbnails of the incoming video in each pipeline in the channel. AUTO turns the feature on, DISABLE turns the feature off.
            type: str
            choices: ['AUTO', 'DISABLED']
      color_correction_settings:
        description:
          - Color Correction Settings
        type: dict
        suboptions:
          global_color_corrections:
            description:
              - An array of colorCorrections that applies when you are using 3D LUT files to perform color conversion on video. Each colorCorrection contains one 3D LUT file (that defines the color mapping for converting an input color space to an output color space), and the input/output combination that this 3D LUT file applies to. MediaLive reads the color space in the input metadata, determines the color space that you have specified for the output, and finds and uses the LUT file that applies to this combination.
            type: list
            elements: dict
            suboptions:
              input_color_space:
                description:
                  - The color space of the input.
                type: str
                choices: ['HDR10', 'HLG_2020', 'REC_601', 'REC_709']
              output_color_space:
                description:
                  - The color space of the output.
                type: str
                choices: ['HDR10', 'HLG_2020', 'REC_601', 'REC_709']
              uri:
                description:
                  - The URI of the 3D LUT file. The protocol must be 's3:' or 's3ssl:':.
                type: str
  input_attachments:
    description:
      - TODO
    type: list
    elements: dict
    suboptions:
      automatic_input_failover_settings:
        description:
          - TODO
        type: dict
        suboptions:
          error_clear_time_msec:
            description:
              - TODO
            type: int
          failover_conditions:
            description:
              - TODO
            type: list
            elements: dict
            suboptions:
              failover_condition_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  audio_silence_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      audio_selector_name:
                        description:
                          - TODO
                        type: str
                      audio_silence_threshold_msec:
                        description:
                          - TODO
                        type: int
                  input_loss_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      input_loss_threshold_msec:
                        description:
                          - TODO
                        type: int
                  video_black_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      black_detect_threshold:
                        description:
                          - TODO
                        type: float
                      video_black_threshold_msec:
                        description:
                          - TODO
                        type: int
          input_preference:
            description:
              - TODO
            type: str
            choices: ['EQUAL_INPUT_PREFERENCE', 'PRIMARY_INPUT_PREFERRED']
          secondary_input_id:
            description:
              - TODO
            type: str
      input_attachment_name:
        description:
          - TODO
        type: str
      input_id:
        description:
          - TODO
        type: str
      input_settings:
        description:
          - TODO
        type: dict
        suboptions:
          audio_selectors:
            description:
              - TODO
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - TODO
                type: str
              selector_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  audio_hls_rendition_selection:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      group_id:
                        description:
                          - TODO
                        type: str
                      name:
                        description:
                          - TODO
                        type: str
                  audio_language_selection:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      language_code:
                        description:
                          - TODO
                        type: str
                      language_selection_policy:
                        description:
                          - TODO
                        type: str
                        choices: ['LOOSE', 'STRICT']
                  audio_pid_selection:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      pid:
                        description:
                          - TODO
                        type: int
                  audio_track_selection:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      tracks:
                        description:
                          - TODO
                        type: list
                        elements: dict
                        suboptions:
                          track:
                            description:
                              - TODO
                            type: int
                      dolby_e_decode:
                        description:
                          - TODO
                        type: dict
                        suboptions:
                          program_selection:
                            description:
                              - TODO
                            type: str
                            choices: ['ALL_CHANNELS', 'PROGRAM_1', 'PROGRAM_2', 'PROGRAM_3', 'PROGRAM_4', 'PROGRAM_5', 'PROGRAM_6', 'PROGRAM_7', 'PROGRAM_8']
          caption_selectors:
            description:
              - TODO
            type: list
            elements: dict
            suboptions:
              language_code:
                description:
                  - TODO
                type: str
              name:
                description:
                  - TODO
                type: str
              selector_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  ancillary_source_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      source_ancillary_channel_number:
                        description:
                          - TODO
                        type: int
                  arib_source_settings:
                    description:
                      - TODO
                    type: dict
                  dvb_sub_source_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      ocr_language:
                        description:
                          - TODO
                        type: str
                        choices: ['DEU', 'ENG', 'FRA', 'NLD', 'POR', 'SPA']
                      pid:
                        description:
                          - TODO
                        type: int
                  embedded_source_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      convert608_to708:
                        description:
                          - TODO
                        type: str
                        choices: ['DISABLED', 'UPCONVERT']
                      scte20_detection:
                        description:
                          - TODO
                        type: str
                        choices: ['AUTO', 'OFF']
                      source608_channel_number:
                        description:
                          - TODO
                        type: int
                      source608_track_number:
                        description:
                          - TODO
                        type: int
                  scte20_source_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      convert608_to708:
                        description:
                          - TODO
                        type: str
                        choices: ['DISABLED', 'UPCONVERT']
                      source608_channel_number:
                        description:
                          - TODO
                        type: int
                  scte27_source_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      ocr_language:
                        description:
                          - TODO
                        type: str
                        choices: ['DEU', 'ENG', 'FRA', 'NLD', 'POR', 'SPA']
                      pid:
                        description:
                          - TODO
                        type: int
                  teletext_source_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      output_rectangle:
                        description:
                          - TODO
                        type: dict
                        suboptions:
                          height:
                            description:
                              - TODO
                            type: float
                          left_offset:
                            description:
                              - TODO
                            type: float
                          top_offset:
                            description:
                              - TODO
                            type: float
                          width:
                            description:
                              - TODO
                            type: float
                      page_number:
                        description:
                          - TODO
                        type: str
          deblock_filter:
            description:
              - TODO
            type: str
            choices: ['DISABLED', 'ENABLED']
          denoise_filter:
            description:
              - TODO
            type: str
            choices: ['DISABLED', 'ENABLED']
          filter_strength:
            description:
              - TODO
            type: int
          input_filter:
            description:
              - TODO
            type: str
            choices: ['AUTO', 'DISABLED', 'FORCED']
          network_input_settings:
            description:
              - TODO
            type: dict
            suboptions:
              hls_input_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  bandwidth:
                    description:
                      - TODO
                    type: int
                  buffer_segments:
                    description:
                      - TODO
                    type: int
                  retries:
                    description:
                      - TODO
                    type: int
                  retry_interval:
                    description:
                      - TODO
                    type: int
                  scte35_source:
                    description:
                      - TODO
                    type: str
                    choices: ['MANIFEST', 'SEGMENTS']
              server_validation:
                description:
                  - TODO
                type: str
                choices: ['CHECK_CRYPTOGRAPHY_AND_VALIDATE_NAME', 'CHECK_CRYPTOGRAPHY_ONLY']
              multicast_input_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  source_ip_address:
                    description:
                      - TODO
                    type: str
          scte35_pid:
            description:
              - TODO
            type: int
          smpte2038_data_preference:
            description:
              - TODO
            type: str
            choices: ['IGNORE', 'PREFER']
          source_end_behavior:
            description:
              - TODO
            type: str
            choices: ['CONTINUE', 'LOOP']
          video_selector:
            description:
              - TODO
            type: dict
            suboptions:
              color_space:
                description:
                  - TODO
                type: str
                choices: ['FOLLOW', 'HDR10', 'HLG_2020', 'REC_601', 'REC_709']
              color_space_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  hdr10_settings:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      max_cll:
                        description:
                          - TODO
                        type: int
                      max_fall:
                        description:
                          - TODO
                        type: int
              color_space_usage:
                description:
                  - TODO
                type: str
                choices: ['FALLBACK', 'FORCE']
              selector_settings:
                description:
                  - TODO
                type: dict
                suboptions:
                  video_selector_pid:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      pid:
                        description:
                          - TODO
                        type: int
                  video_selector_program_id:
                    description:
                      - TODO
                    type: dict
                    suboptions:
                      program_id:
                        description:
                          - TODO
                        type: int
      logical_interface_names:
        description:
          - A list of logical interface names used for network isolation in MediaLive Anywhere deployments.
        type: list
        elements: str
  input_specification:
    description:
      - TODO
    type: dict
    suboptions:
      codec:
        description:
          - TODO
        type: str
        choices: ['MPEG2', 'AVC', 'HEVC']
      maximum_bitrate:
        description:
          - TODO
        type: str
        choices: ['MAX_10_MBPS', 'MAX_20_MBPS', 'MAX_50_MBPS']
      resolution:
        description:
          - TODO
        type: str
        choices: ['SD', 'HD', 'UHD']
  log_level:
    description:
      - TODO
    type: str
    choices: ['ERROR', 'WARNING', 'INFO', 'DEBUG', 'DISABLED']
  maintenance:
    description:
      - TODO
    type: dict
    suboptions:
      maintenance_day:
        description:
          - TODO
        type: str
        choices: ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
      maintenance_start_time:
        description:
          - TODO
        type: str
  name:
    description:
      - TODO
    type: str
  request_id:
    description:
      - TODO
    type: str
  reserved:
    description:
      - TODO
    type: str
  role_arn:
    description:
      - TODO
    type: str
  tags:
    description:
      - TODO
    type: dict
  vpc:
    description:
      - TODO
    type: dict
    suboptions:
      public_address_allocation_ids:
        description:
          - TODO
        type: list
        elements: str
      security_group_ids:
        description:
          - TODO
        type: list
        elements: str
      subnet_ids:
        description:
          - TODO
        type: list
        elements: str
  anywhere_settings:
    description:
      - TODO
    type: dict
    suboptions:
      channel_placement_group_id:
        description:
          - TODO
        type: str
      cluster_id:
        description:
          - TODO
        type: str
  channel_engine_version:
    description:
      - TODO
    type: dict
    suboptions:
      version:
        description:
          - TODO
        type: str
  dry_run:
    description:
      - TODO
    type: bool

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
  - amazon.aws.tags
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

import uuid
from typing import Dict

try:
    from botocore.exceptions import WaiterError, ClientError, BotoCoreError
except ImportError:
    pass # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict, camel_dict_to_snake_dict, recursive_diff
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError
from ansible_collections.amazon.aws.plugins.module_utils.tagging import compare_aws_tags


class MedialiveAnsibleAWSError(AnsibleAWSError):
    pass

class MediaLiveChannelManager:
    '''Manage AWS MediaLive Anywhere Channels'''

    def __init__(self, module: AnsibleAWSModule):
        '''
        Initialize the MediaLiveChannelManager

        Args:
            module: AnsibleAWSModule instance
        '''
        self.module = module
        self.client = self.module.client('medialive')
        self._channel = {}
        self.changed = False

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, channel: Dict):
        channel = camel_dict_to_snake_dict(channel)
        if channel.get('response_metadata'):
            del channel['response_metadata']
        if channel.get('id'):
            channel['channel_id'] = channel.get('id')
            del channel['id']
        self._channel = channel


    def do_create_channel(self, params):
        """
        Create a new MediaLive Channel
        
        Args:
            params: Parameters for Channel creation
        """
        allowed_params = [
            'channel_id',
            'name',
            'cdi_input_specification',
            'channel_class',
            'destinations',
            'encoder_settings',
            'input_attachments',
            'input_specification',
            'log_level',
            'maintenance',
            'reserved',
            'role_arn',
            'vpc',
            'anywhere_settings',
            'channel_engine_version',
            'dry_run',
            'tags',
            'request_id'
        ]
        required_params = ['name']

        for param in required_params:
            if not params.get(param):
                raise MedialiveAnsibleAWSError(message=f'The {param} parameter is required when creating a new Channel')

        create_params = { k: v for k, v in params.items() if k in allowed_params and v }
        create_params = self.clean_up(create_params)

        tags = create_params.get('tags') # To preserve case in tag keys
        create_params = snake_dict_to_camel_dict(create_params, capitalize_first=True)

        if tags and create_params:
            create_params['Tags'] = tags

        try:
            self.channel = self.client.create_channel(**create_params)['Channel']  # type: ignore
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to create Medialive Channel',
                exception=e
            )


    def do_update_channel(self, params):
        """
        Update a new MediaLive Channel
        
        Args:
            params: Parameters for Channel update
        """
        if not params.get('channel_id'):
            raise MedialiveAnsibleAWSError(message='The channel_id parameter is required during channel update.')

        tags = params.get('tags')
        purge_tags = params.get('purge_tags')
        del params['tags']
        del params['purge_tags']

        allowed_params = [
            'cdi_input_specification',
            'channel_id',
            'destinations',
            'encoder_settings',
            'input_attachments',
            'input_specification',
            'log_level',
            'maintenance',
            'name',
            'role_arn',
            'channel_engine_version',
            'dry_run',
            'anywhere_settings'
        ]

        #  current_params = { k: v for k, v in self.channel.items() if k in allowed_params }
        update_params = { k: v for k, v in params.items() if k in allowed_params and v }
        update_params = self.clean_up(update_params)

        current_params = {}
        for k, v in self.channel.items():
            if k in allowed_params and k in update_params:
                current_params[k] = v

        # Short circuit
        if not recursive_diff(current_params, update_params):
            return

        try:
            if recursive_diff(current_params, update_params):
                update_params = snake_dict_to_camel_dict(update_params, capitalize_first=True)
                self.channel = self.client.update_channel(**update_params)['Channel']  # type: ignore
                self.changed = True
            if tags and self._update_tags(tags, purge_tags):
                self.channel = self.get_channel_by_id(self.channel['channel_id']) # type: ignore
                self.changed = True

        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to update Medialive Channel',
                exception=e
            )

    def get_channel_by_name(self, name: str):
        """
        Find a Channel by name

        Args:
            name: The name of the Channel to find
        """

        try:
            paginator = self.client.get_paginator('list_channels')  # type: ignore
            found = []
            for page in paginator.paginate():
                for channel in page.get('Channels', []):
                    if channel.get('Name') == name:
                        found.append(channel.get('Id'))
            if len(found) > 1:
                raise MedialiveAnsibleAWSError(message='Found more than one Channels under the same name')
            elif len(found) == 1:
                self.get_channel_by_id(found[0])

        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to get Medialive Channel',
                exception=e
            )

    def get_channel_by_id(self, channel_id: str):
        """
        Get a Channel by ID

        Args:
            channel_id: The ID of the Channel to retrieve
        """
        try:
            self.channel = self.client.describe_channel(ChannelId=channel_id)  # type: ignore
        except is_boto3_error_code('ResourceNotFoundException'):
            self.channel = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to get Medialive Channel',
                exception=e
            )

    def delete_channel(self, channel_id: str):
        """
        Delete a MediaLive Channel
        
        Args:
            channel_id: ID of the Channel to delete
        """
        try:
            self.client.delete_channel(ChannelId=channel_id)  # type: ignore
            self.channel = {}
            self.changed = True
        except is_boto3_error_code('ResourceNotFoundException'):
            self.channel = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to delete Medialive Channel',
                exception=e
            )

    def wait_for(self, want: str, channel_id: str, wait_timeout: int = 60):
        """
        Invoke one of the custom waiters and wait

        Args:
            want: one of 'channel_created'|'channel_deleted'|'channel_running'|'channel_stopped'
            channel_id: the ID of the Channel
            wait_timeout: the maximum amount of time to wait in seconds (default: 60)
        """

        try:
            waiter = self.client.get_waiter(want) # type: ignore
            config = {
                'Delay': min(5, wait_timeout),
                'MaxAttempts': wait_timeout // 5
            }
            waiter.wait(
                ChannelId=channel_id,
                WaiterConfig=config
            )
        except WaiterError as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message=f'Timeout waiting for Channel {channel_id}',
                exception=e
            )

    def _update_tags(self, tags: dict, purge: bool) -> bool:
        """
        Takes care of updating Channel tags

        Args:
            tags: a dict of tags supplied by the user
            purge: whether or not to delete existing tags that aren't in the tags dict
        Returns:
            True if tags were updated, otherwise False
        """

        # Short-circuit
        if self.module.check_mode:
            return False

        to_add, to_delete = compare_aws_tags(self.channel['tags'], tags, purge)

        if not any((to_add, to_delete)):
            return False

        try:
            if to_add:
                self.client.create_tags(ResourceArn=self.channel['arn'], Tags=to_add) # type: ignore
            if to_delete:
                self.client.delete_tags(ResourceArn=self.channel['arn'], TagKeys=to_delete) # type: ignore
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to update MediaLive Channel resource Tags',
                exception=e
            )

        return True

    @staticmethod
    def clean_up(data):
        if isinstance(data, dict):
            return {
                key: MediaLiveChannelManager.clean_up(value)
                for key, value in data.items()
                if value is not None and MediaLiveChannelManager.clean_up(value) is not None
            }
        elif isinstance(data, list):
            cleaned = [
                MediaLiveChannelManager.clean_up(item)
                for item in data
                if item is not None and MediaLiveChannelManager.clean_up(item) is not None
            ]
            # Return None if the list is empty, otherwise return the cleaned list
            return cleaned if cleaned else None
        else:
            return data

def get_arg(arg:str, params:dict, spec:dict):
    if arg in spec.keys():
        aliases = spec[arg].get('aliases', [])
        for k, v in params.items():
            if k in [arg, *aliases] and v:
                return v

def main():
    """Main entry point for the module"""
    argument_spec = dict(
        name=dict(type='str', aliases=['channel_name']),
        id=dict(type='str', aliases=['channel_id']),
        cdi_input_specification=dict(
            type='dict',
            options=dict(
                resolution=dict(
                    type='str',
                    choices=['SD', 'HD', 'FHD', 'UHD'],
                )
            ),
        ),
        channel_class=dict(
            type='str',
            choices=['STANDARD', 'SINGLE_PIPELINE'],
        ),
        destinations=dict(
            type='list',
            elements='dict',
            options=dict(
                id=dict(type='str'),
                media_package_settings=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        channel_id=dict(type='str'),
                        channel_group=dict(type='str'),
                        channel_name=dict(type='str')
                    )
                ),
                multiplex_settings=dict(
                    type='dict',
                    options=dict(
                        multiplex_id=dict(type='str'),
                        program_name=dict(type='str')
                    )
                ),
                settings=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        password_param=dict(type='str'),
                        stream_name=dict(type='str'),
                        url=dict(type='str'),
                        username=dict(type='str')
                    )
                ),
                srt_settings=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        encryption_passphrase_secret_arn=dict(type='str'),
                        stream_id=dict(type='str'),
                        url=dict(type='str')
                    )
                ),
                logical_interface_names=dict(type='list', elements='str')
            )
        ),
        encoder_settings=dict(
            type='dict',
            options=dict(
                audio_descriptions=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        audio_normalization_settings=dict(
                            type='dict',
                            options=dict(
                                algorithm=dict(type='str', choices=['ITU_1770_1', 'ITU_1770_2']),
                                algorithm_control=dict(type='str', choices=['CORRECT_AUDIO']),
                                target_lkfs=dict(type='float')
                            )
                        ),
                        audio_selector_name=dict(type='str'),
                        audio_type=dict(
                            type='str',
                            choices=['CLEAN_EFFECTS', 'HEARING_IMPAIRED', 'UNDEFINED', 'VISUAL_IMPAIRED_COMMENTARY'],
                        ),
                        audio_type_control=dict(type='str', choices=['FOLLOW_INPUT', 'USE_CONFIGURED']),
                        audio_watermarking_settings=dict(
                            type='dict',
                            options=dict(
                                nielsen_watermarks_settings=dict(
                                    type='dict',
                                    options=dict(
                                        nielsen_cbet_settings=dict(
                                            type='dict',
                                            options=dict(
                                                cbet_check_digit_string=dict(type='str'),
                                                cbet_stepaside=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                                csid=dict(type='str')
                                            )
                                        )
                                    )
                                ),
                                nielsen_distribution_type=dict(
                                    type='str',
                                    choices=['FINAL_DISTRIBUTOR', 'PROGRAM_CONTENT']),
                                nielsen_naes_ii_nw_settings=dict(
                                    type='dict',
                                    options=dict(
                                        check_digit_string=dict(type='str'),
                                        sid=dict(type='float'),
                                        timezone=dict(
                                            type='str',
                                            choices=[
                                                'AMERICA_PUERTO_RICO',
                                                'US_ALASKA',
                                                'US_ARIZONA',
                                                'US_CENTRAL',
                                                'US_EASTERN',
                                                'US_HAWAII',
                                                'US_MOUNTAIN',
                                                'US_PACIFIC',
                                                'US_SAMOA',
                                                'UTC',
                                            ]
                                        )
                                    )
                                )
                            )
                        ),
                        codec_settings=dict(
                            type='dict',
                            options=dict(
                                aac_settings=dict(
                                    type='dict',
                                    options=dict(
                                        bitrate=dict(type='float'),
                                        coding_mode=dict(
                                            type='str',
                                            choices=[
                                                'AD_RECEIVER_MIX',
                                                'CODING_MODE_1_0',
                                                'CODING_MODE_1_1',
                                                'CODING_MODE_2_0',
                                                'CODING_MODE_5_1',
                                            ]
                                        ),
                                        input_type=dict(type='str', choices=['BROADCASTER_MIXED_AD', 'NORMAL']),
                                        profile=dict(type='str', choices=['HEV1', 'HEV2', 'LC']),
                                        rate_control_mode=dict(type='str', choices=['CBR', 'VBR']),
                                        raw_format=dict(type='str', choices=['LATM_LOAS', 'NONE']),
                                        sample_rate=dict(type='float'),
                                        spec=dict(type='str', choices=['MPEG2', 'MPEG4']),
                                        vbr_quality=dict(type='str', choices=['HIGH', 'LOW', 'MEDIUM_HIGH', 'MEDIUM_LOW'])
                                    )
                                ),
                                ac3_settings=dict(
                                    type='dict',
                                    options=dict(
                                        bitrate=dict(type='float'),
                                        bitstream_mode=dict(
                                            type='str',
                                            choices=[
                                                'COMMENTARY',
                                                'COMPLETE_MAIN',
                                                'DIALOGUE',
                                                'EMERGENCY',
                                                'HEARING_IMPAIRED',
                                                'MUSIC_AND_EFFECTS',
                                                'VISUALLY_IMPAIRED',
                                                'VOICE_OVER',
                                            ]
                                        ),
                                        coding_mode=dict(
                                            type='str',
                                            choices=[
                                                'CODING_MODE_1_0',
                                                'CODING_MODE_1_1',
                                                'CODING_MODE_2_0',
                                                'CODING_MODE_3_2_LFE'
                                            ],
                                        ),
                                        dialnorm=dict(type='float'),
                                        drc_profile=dict(type='str', choices=['FILM_STANDARD', 'NONE']),
                                        lfe_filter=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        metadata_control=dict(type='str', choices=['FOLLOW_INPUT', 'USE_CONFIGURED']),
                                        attenuation_control=dict(type='str', choices=['ATTENUATE_3_DB', 'NONE'])
                                    )
                                ),
                                eac3_atmos_settings=dict(
                                    type='dict',
                                    options=dict(
                                        bitrate=dict(type='float'),
                                        coding_mode=dict(type='str', choices=['CODING_MODE_5_1_4', 'CODING_MODE_7_1_4', 'CODING_MODE_9_1_6']),
                                        dialnorm=dict(type='int'),
                                        drc_line=dict(
                                            type='str',
                                            choices=[
                                                'FILM_LIGHT',
                                                'FILM_STANDARD',
                                                'MUSIC_LIGHT',
                                                'MUSIC_STANDARD',
                                                'NONE',
                                                'SPEECH',
                                            ]
                                        ),
                                        drc_rf=dict(
                                            type='str',
                                            choices=[
                                                'FILM_LIGHT',
                                                'FILM_STANDARD',
                                                'MUSIC_LIGHT',
                                                'MUSIC_STANDARD',
                                                'NONE',
                                                'SPEECH',
                                            ]
                                        ),
                                        height_trim=dict(type='float'),
                                        surround_trim=dict(type='float')
                                    )
                                ),
                                eac3_settings=dict(
                                    type='dict',
                                    options=dict(
                                        attenuation_control=dict(type='str', choices=['ATTENUATE_3_DB', 'NONE']),
                                        bitrate=dict(type='float'),
                                        bitstream_mode=dict(
                                            type='str',
                                            choices=[
                                                'COMMENTARY',
                                                'COMPLETE_MAIN',
                                                'EMERGENCY',
                                                'HEARING_IMPAIRED',
                                                'VISUALLY_IMPAIRED',
                                            ]
                                        ),
                                        coding_mode=dict(type='str', choices=['CODING_MODE_1_0', 'CODING_MODE_2_0', 'CODING_MODE_3_2']),
                                        dc_filter=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        dialnorm=dict(type='float'),
                                        drc_line=dict(
                                            type='str',
                                            choices=['FILM_LIGHT', 'FILM_STANDARD', 'MUSIC_LIGHT', 'MUSIC_STANDARD', 'NONE', 'SPEECH']
                                        ),
                                        drc_rf=dict(
                                            type='str',
                                            choices=['FILM_LIGHT', 'FILM_STANDARD', 'MUSIC_LIGHT', 'MUSIC_STANDARD', 'NONE', 'SPEECH']
                                        ),
                                        lfe_control=dict(type='str', choices=['LFE', 'NO_LFE']),
                                        lfe_filter=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        lo_ro_center_mix_level=dict(type='float'),
                                        lo_ro_surround_mix_level=dict(type='float'),
                                        lt_rt_center_mix_level=dict(type='float'),
                                        lt_rt_surround_mix_level=dict(type='float'),
                                        metadata_control=dict(type='str', choices=['FOLLOW_INPUT', 'USE_CONFIGURED']),
                                        passthrough_control=dict(type='str', choices=['NO_PASSTHROUGH', 'WHEN_POSSIBLE']),
                                        phase_control=dict(type='str', choices=['NO_SHIFT', 'SHIFT_90_DEGREES']),
                                        stereo_downmix=dict(type='str', choices=['DPL2', 'LO_RO', 'LT_RT', 'NOT_INDICATED']),
                                        surround_ex_mode=dict(type='str', choices=['DISABLED', 'ENABLED', 'NOT_INDICATED']),
                                        surround_mode=dict(type='str', choices=['DISABLED', 'ENABLED', 'NOT_INDICATED'])
                                    )
                                ),
                                mp2_settings=dict(
                                    type='dict',
                                    options=dict(
                                        bitrate=dict(type='float'),
                                        coding_mode=dict(type='str', choices=['CODING_MODE_1_0', 'CODING_MODE_2_0']),
                                        sample_rate=dict(type='float')
                                    )
                                ),
                                pass_through_settings=dict(type='dict'),
                                wav_settings=dict(
                                    type='dict',
                                    options=dict(
                                        bit_depth=dict(type='float'),
                                        coding_mode=dict(type='str', choices=['CODING_MODE_1_0', 'CODING_MODE_2_0', 'CODING_MODE_4_0', 'CODING_MODE_8_0']),
                                        sample_rate=dict(type='float')
                                    )
                                )
                            )
                        ),
                        language_code=dict(type='str'),
                        language_code_control=dict(type='str', choices=['FOLLOW_INPUT', 'USE_CONFIGURED']),
                        name=dict(type='str'),
                        remix_settings=dict(
                            type='dict',
                            options=dict(
                                channel_mappings=dict(
                                    type='list',
                                    elements='dict',
                                    options=dict(
                                        input_channel_levels=dict(
                                            type='list',
                                            elements='dict',
                                            options=dict(
                                                gain=dict(type='int'),
                                                input_channel=dict(type='int')
                                            )
                                        ),
                                        output_channel=dict(type='int')
                                    )
                                ),
                                channels_in=dict(type='int'),
                                channels_out=dict(type='int')
                            )
                        ),
                        stream_name=dict(type='str'),
                        audio_dash_roles=dict(
                            type='list',
                            elements='str',
                            choices=[
                                'ALTERNATE',
                                'COMMENTARY',
                                'DESCRIPTION',
                                'DUB',
                                'EMERGENCY',
                                'ENHANCED-AUDIO-INTELLIGIBILITY',
                                'KARAOKE',
                                'MAIN',
                                'SUPPLEMENTARY',
                            ]
                        ),
                        dvb_dash_accessibility=dict(
                            type='str',
                            choices=[
                                'DVBDASH_1_VISUALLY_IMPAIRED',
                                'DVBDASH_2_HARD_OF_HEARING',
                                'DVBDASH_3_SUPPLEMENTAL_COMMENTARY',
                                'DVBDASH_4_DIRECTORS_COMMENTARY',
                                'DVBDASH_5_EDUCATIONAL_NOTES',
                                'DVBDASH_6_MAIN_PROGRAM',
                                'DVBDASH_7_CLEAN_FEED',
                            ]
                        )
                    )
                ),
                avail_blanking=dict(
                    type='dict',
                    options=dict(
                        avail_blanking_image=dict(
                            type='dict',
                            options=dict(
                                password_param=dict(type='str'),
                                uri=dict(type='str'),
                                username=dict(type='str')
                            )
                        ),
                        state=dict(type='str', choices=['DISABLED', 'ENABLED'])
                    )
                ),
                avail_configuration=dict(
                    type='dict',
                    options=dict(
                        avail_settings=dict(
                            type='dict',
                            options=dict(
                                esam=dict(
                                    type='dict',
                                    options=dict(
                                        acquisition_point_id=dict(type='str'),
                                        ad_avail_offset=dict(type='int'),
                                        password_param=dict(type='str'),
                                        pois_endpoint=dict(type='str'),
                                        username=dict(type='str'),
                                        zone_identity=dict(type='str')
                                    )
                                ),
                                scte35_splice_insert=dict(
                                    type='dict',
                                    options=dict(
                                        ad_avail_offset=dict(type='int'),
                                        no_regional_blackout_flag=dict(type='str', choices=['FOLLOW', 'IGNORE']),
                                        web_delivery_allowed_flag=dict(type='str', choices=['FOLLOW', 'IGNORE'])
                                    )
                                ),
                                scte35_time_signal_apos=dict(
                                    type='dict',
                                    options=dict(
                                        ad_avail_offset=dict(type='int'),
                                        no_regional_blackout_flag=dict(type='str', choices=['FOLLOW', 'IGNORE']),
                                        web_delivery_allowed_flag=dict(type='str', choices=['FOLLOW', 'IGNORE'])
                                    )
                                )
                            )
                        ),
                        scte35_segmentation_scope=dict(type='str', choices=['ALL_OUTPUT_GROUPS', 'SCTE35_ENABLED_OUTPUT_GROUPS'])
                    )
                ),
                blackout_slate=dict(
                    type='dict',
                    options=dict(
                        blackout_slate_image=dict(
                            type='dict',
                            options=dict(
                                password_param=dict(type='str'),
                                uri=dict(type='str'),
                                username=dict(type='str')
                            )
                        ),
                        network_end_blackout=dict(type='str', choices=['DISABLED', 'ENABLED']),
                        network_end_blackout_image=dict(
                            type='dict',
                            options=dict(
                                password_param=dict(type='str'),
                                uri=dict(type='str'),
                                username=dict(type='str')
                            )
                        ),
                        network_id=dict(type='str'),
                        state=dict(type='str', choices=['DISABLED', 'ENABLED'])
                    )
                ),
                caption_descriptions=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        accessibility=dict(type='str', choices=['DOES_NOT_IMPLEMENT_ACCESSIBILITY_FEATURES', 'IMPLEMENTS_ACCESSIBILITY_FEATURES']),
                        caption_selector_name=dict(type='str'),
                        destination_settings=dict(
                            type='dict',
                            options=dict(
                                arib_destination_settings=dict(type='dict'),
                                burn_in_destination_settings=dict(
                                    type='dict',
                                    options=dict(
                                        alignment=dict(type='str', choices=['CENTERED', 'LEFT', 'SMART']),
                                        background_color=dict(type='str', choices=['BLACK', 'NONE', 'WHITE']),
                                        background_opacity=dict(type='int'),
                                        font=dict(
                                            type='dict',
                                            options=dict(
                                                password_param=dict(type='str'),
                                                uri=dict(type='str'),
                                                username=dict(type='str')
                                            )
                                        ),
                                        font_color=dict(type='str', choices=['BLACK', 'BLUE', 'GREEN', 'RED', 'WHITE', 'YELLOW']),
                                        font_opacity=dict(type='int'),
                                        font_resolution=dict(type='int'),
                                        font_size=dict(type='str'),
                                        outline_color=dict(type='str', choices=['BLACK', 'BLUE', 'GREEN', 'RED', 'WHITE', 'YELLOW']),
                                        outline_size=dict(type='int'),
                                        shadow_color=dict(type='str', choices=['BLACK', 'NONE', 'WHITE']),
                                        shadow_opacity=dict(type='int'),
                                        shadow_x_offset=dict(type='int'),
                                        shadow_y_offset=dict(type='int'),
                                        teletext_grid_control=dict(type='str', choices=['FIXED', 'SCALED']),
                                        x_position=dict(type='int'),
                                        y_position=dict(type='int')
                                    )
                                ),
                                dvb_sub_destination_settings=dict(
                                    type='dict',
                                    options=dict(
                                        alignment=dict(type='str', choices=['CENTERED', 'LEFT', 'SMART']),
                                        background_color=dict(type='str', choices=['BLACK', 'NONE', 'WHITE']),
                                        background_opacity=dict(type='int'),
                                        font=dict(
                                            type='dict',
                                            options=dict(
                                                password_param=dict(type='str'),
                                                uri=dict(type='str'),
                                                username=dict(type='str'))),
                                        font_color=dict(
                                            type='str',
                                            choices=[
                                                'BLACK',
                                                'BLUE',
                                                'GREEN',
                                                'RED',
                                                'WHITE',
                                                'YELLOW',
                                            ]
                                        ),
                                        font_opacity=dict(type='int'),
                                        font_resolution=dict(type='int'),
                                        font_size=dict(type='str'),
                                        outline_color=dict(
                                            type='str',
                                            choices=[
                                                'BLACK',
                                                'BLUE',
                                                'GREEN',
                                                'RED',
                                                'WHITE',
                                                'YELLOW',
                                            ]
                                        ),
                                        outline_size=dict(type='int'),
                                        shadow_color=dict(type='str', choices=['BLACK', 'NONE', 'WHITE']),
                                        shadow_opacity=dict(type='int'),
                                        shadow_x_offset=dict(type='int'),
                                        shadow_y_offset=dict(type='int'),
                                        teletext_grid_control=dict(type='str', choices=['FIXED', 'SCALED']),
                                        x_position=dict(type='int'),
                                        y_position=dict(type='int')
                                    )
                                ),
                                ebu_tt_d_destination_settings=dict(
                                    type='dict',
                                    options=dict(
                                        copyright_holder=dict(type='str'),
                                        fill_line_gap=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        font_family=dict(type='str'),
                                        style_control=dict(type='str', choices=['EXCLUDE', 'INCLUDE']),
                                        default_font_size=dict(type='int'),
                                        default_line_height=dict(type='int')
                                    )
                                ),
                                embedded_destination_settings=dict(type='dict'),
                                embedded_plus_scte20_destination_settings=dict(type='dict'),
                                rtmp_caption_info_destination_settings=dict(type='dict'),
                                scte20_plus_embedded_destination_settings=dict(type='dict'),
                                scte27_destination_settings=dict(type='dict'),
                                smpte_tt_destination_settings=dict(type='dict'),
                                teletext_destination_settings=dict(type='dict'),
                                ttml_destination_settings=dict(
                                    type='dict',
                                    options=dict(
                                        style_control=dict(type='str', choices=['PASSTHROUGH', 'USE_CONFIGURED'])
                                    )
                                ),
                                webvtt_destination_settings=dict(
                                    type='dict',
                                    options=dict(
                                        style_control=dict(type='str', choices=['NO_STYLE_DATA', 'PASSTHROUGH'])
                                    )
                                )
                            )
                        ),
                        language_code=dict(type='str'),
                        name=dict(type='str'),
                        caption_dash_roles=dict(
                            type='list',
                            elements='str',
                            choices=[
                                'ALTERNATE',
                                'CAPTION',
                                'COMMENTARY',
                                'DESCRIPTION',
                                'DUB',
                                'EASYREADER',
                                'EMERGENCY',
                                'FORCED-SUBTITLE',
                                'KARAOKE',
                                'MAIN',
                                'METADATA',
                                'SUBTITLE',
                                'SUPPLEMENTARY',
                            ]
                        ),
                        dvb_dash_accessibility=dict(
                            type='str',
                            choices=[
                                'DVBDASH_1_VISUALLY_IMPAIRED',
                                'DVBDASH_2_HARD_OF_HEARING',
                                'DVBDASH_3_SUPPLEMENTAL_COMMENTARY',
                                'DVBDASH_4_DIRECTORS_COMMENTARY',
                                'DVBDASH_5_EDUCATIONAL_NOTES',
                                'DVBDASH_6_MAIN_PROGRAM',
                                'DVBDASH_7_CLEAN_FEED',
                            ]
                        )
                    )
                ),
                feature_activations=dict(
                    type='dict',
                    options=dict(
                        input_prepare_schedule_actions=dict(type='str', choices=['DISABLED', 'ENABLED']),
                        output_static_image_overlay_schedule_actions=dict(type='str', choices=['DISABLED', 'ENABLED'])
                    )
                ),
                global_configuration=dict(
                    type='dict',
                    options=dict(
                        initial_audio_gain=dict(type='int'),
                        input_end_action=dict(type='str', choices=['NONE', 'SWITCH_AND_LOOP_INPUTS']),
                        input_loss_behavior=dict(
                            type='dict',
                            options=dict(
                                black_frame_msec=dict(type='int'),
                                input_loss_image_color=dict(type='str'),
                                input_loss_image_slate=dict(
                                    type='dict',
                                    options=dict(
                                        password_param=dict(type='str'),
                                        uri=dict(type='str'),
                                        username=dict(type='str')
                                    )
                                ),
                                input_loss_image_type=dict(type='str', choices=['COLOR', 'SLATE']),
                                repeat_frame_msec=dict(type='int')
                            )
                        ),
                        output_locking_mode=dict(type='str', choices=['EPOCH_LOCKING', 'PIPELINE_LOCKING', 'DISABLED']),
                        output_timing_source=dict(type='str', choices=['INPUT_CLOCK', 'SYSTEM_CLOCK']),
                        support_low_framerate_inputs=dict(type='str', choices=['DISABLED', 'ENABLED']),
                        output_locking_settings=dict(
                            type='dict',
                            options=dict(
                                epoch_locking_settings=dict(
                                    type='dict',
                                    options=dict(
                                        custom_epoch=dict(type='str'),
                                        jam_sync_time=dict(type='str')
                                    )
                                ),
                                pipeline_locking_settings=dict(type='dict')
                            )
                        )
                    )
                ),
                motion_graphics_configuration=dict(
                    type='dict',
                    options=dict(
                        motion_graphics_insertion=dict(type='str', choices=['DISABLED', 'ENABLED']),
                        motion_graphics_settings=dict(
                            type='dict',
                            options=dict(
                                html_motion_graphics_settings=dict(type='dict')
                            )
                        )
                    )
                ),
                nielsen_configuration=dict(
                    type='dict',
                    options=dict(
                        distributor_id=dict(type='str'),
                        nielsen_pcm_to_id3_tagging=dict(type='str', choices=['DISABLED', 'ENABLED'])
                    )
                ),
                output_groups=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        name=dict(type='str'),
                        output_group_settings=dict(
                            type='dict',
                            options=dict(
                                archive_group_settings=dict(
                                    type='dict',
                                    options=dict(
                                        archive_cdn_settings=dict(
                                            type='dict',
                                            options=dict(
                                                archive_s3_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        canned_acl=dict(
                                                            type='str',
                                                            choices=[
                                                                'AUTHENTICATED_READ',
                                                                'BUCKET_OWNER_FULL_CONTROL',
                                                                'BUCKET_OWNER_READ',
                                                                'PUBLIC_READ',
                                                            ]
                                                        )
                                                    )
                                                )
                                            )
                                        ),
                                        destination=dict(
                                            type='dict',
                                            options=dict(
                                                destination_ref_id=dict(type='str')
                                            )
                                        ),
                                        rollover_interval=dict(type='int')
                                    )
                                ),
                                frame_capture_group_settings=dict(
                                    type='dict',
                                    options=dict(
                                        destination=dict(
                                            type='dict',
                                            options=dict(
                                                destination_ref_id=dict(type='str')
                                            )
                                        ),
                                        frame_capture_cdn_settings=dict(
                                            type='dict',
                                            options=dict(
                                                frame_capture_s3_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        canned_acl=dict(
                                                            type='str',
                                                            choices=[
                                                                'AUTHENTICATED_READ',
                                                                'BUCKET_OWNER_FULL_CONTROL',
                                                                'BUCKET_OWNER_READ',
                                                                'PUBLIC_READ',
                                                            ]
                                                        )
                                                    )
                                                )
                                            )
                                        )
                                    )
                                ),
                                hls_group_settings=dict(
                                    type='dict',
                                    options=dict(
                                        ad_markers=dict(type='list', elements='str', choices=['ADOBE', 'ELEMENTAL', 'ELEMENTAL_SCTE35']),
                                        base_url_content=dict(type='str'),
                                        base_url_content1=dict(type='str'),
                                        base_url_manifest=dict(type='str'),
                                        base_url_manifest1=dict(type='str'),
                                        caption_language_mappings=dict(
                                            type='list',
                                            elements='dict',
                                            options=dict(
                                                caption_channel=dict(type='int'),
                                                language_code=dict(type='str', )
                                            )
                                        ),
                                        caption_language_setting=dict(type='str', choices=['INSERT', 'NONE', 'OMIT']),
                                        client_cache=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        codec_specification=dict(type='str', choices=['RFC_4281', 'RFC_6381']),
                                        constant_iv=dict(type='str'),
                                        destination=dict(
                                            type='dict',
                                            options=dict(
                                                destination_ref_id=dict(type='str')
                                            )
                                        ),
                                        directory_structure=dict(type='str', choices=['SINGLE_DIRECTORY', 'SUBDIRECTORY_PER_STREAM']),
                                        discontinuity_tags=dict(type='str', choices=['INSERT', 'NEVER_INSERT']),
                                        encryption_type=dict(type='str', choices=['AES128', 'SAMPLE_AES']),
                                        hls_cdn_settings=dict(
                                            type='dict',
                                            options=dict(
                                                hls_akamai_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        connection_retry_interval=dict(type='int'),
                                                        filecache_duration=dict(type='int'),
                                                        http_transfer_mode=dict(type='str', choices=['CHUNKED', 'NON_CHUNKED']),
                                                        num_retries=dict(type='int'),
                                                        restart_delay=dict(type='int'),
                                                        salt=dict(type='str'),
                                                        token=dict(type='str')
                                                    )
                                                ),
                                                hls_basic_put_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        connection_retry_interval=dict(type='int'),
                                                        filecache_duration=dict(type='int'),
                                                        num_retries=dict(type='int'),
                                                        restart_delay=dict(type='int')
                                                    )
                                                ),
                                                hls_media_store_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        connection_retry_interval=dict(type='int'),
                                                        filecache_duration=dict(type='int'),
                                                        media_store_storage_class=dict(type='str', choices=['TEMPORAL']),
                                                        num_retries=dict(type='int'),
                                                        restart_delay=dict(type='int')
                                                    )
                                                ),
                                                hls_s3_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        canned_acl=dict(type='str', choices=['AUTHENTICATED_READ', 'BUCKET_OWNER_FULL_CONTROL', 'BUCKET_OWNER_READ', 'PUBLIC_READ'])
                                                    )
                                                ),
                                                hls_webdav_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        connection_retry_interval=dict(type='int'),
                                                        filecache_duration=dict(type='int'),
                                                        http_transfer_mode=dict(type='str', choices=['CHUNKED', 'NON_CHUNKED']),
                                                        num_retries=dict(type='int'),
                                                        restart_delay=dict(type='int')
                                                    )
                                                )
                                            )
                                        ),
                                        hls_id3_segment_tagging=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        i_frame_only_playlists=dict(type='str', choices=['DISABLED', 'STANDARD']),
                                        incomplete_segment_behavior=dict(type='str', choices=['AUTO', 'SUPPRESS']),
                                        index_n_segments=dict(type='int'),
                                        input_loss_action=dict(type='str', choices=['EMIT_OUTPUT', 'PAUSE_OUTPUT']),
                                        iv_in_manifest=dict(type='str', choices=['EXCLUDE', 'INCLUDE']),
                                        iv_source=dict(type='str', choices=['EXPLICIT', 'FOLLOWS_SEGMENT_NUMBER']),
                                        keep_segments=dict(type='int'),
                                        key_format=dict(type='str'),
                                        key_format_versions=dict(type='str'),
                                        key_provider_settings=dict(
                                            type='dict',
                                            options=dict(
                                                static_key_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        key_provider_server=dict(
                                                            type='dict',
                                                            options=dict(
                                                                password_param=dict(type='str'),
                                                                uri=dict(type='str'),
                                                                username=dict(type='str')
                                                            )
                                                        ),
                                                        static_key_value=dict(type='str')
                                                    )
                                                )
                                            )
                                        ),
                                        manifest_compression=dict(type='str', choices=['GZIP', 'NONE']),
                                        manifest_duration_format=dict(type='str', choices=['FLOATING_POINT', 'INTEGER']),
                                        min_segment_length=dict(type='int'),
                                        mode=dict(type='str', choices=['LIVE', 'VOD']),
                                        output_selection=dict(type='str', choices=['MANIFESTS_AND_SEGMENTS', 'SEGMENTS_ONLY', 'VARIANT_MANIFESTS_AND_SEGMENTS']),
                                        program_date_time=dict(type='str', choices=['EXCLUDE', 'INCLUDE']),
                                        program_date_time_clock=dict(type='str', choices=['INITIALIZE_FROM_OUTPUT_TIMECODE', 'SYSTEM_CLOCK']),
                                        program_date_time_period=dict(type='int'),
                                        redundant_manifest=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        segment_length=dict(type='int'),
                                        segmentation_mode=dict(type='str', choices=['USE_INPUT_SEGMENTATION', 'USE_SEGMENT_DURATION']),
                                        segments_per_subdirectory=dict(type='int'),
                                        stream_inf_resolution=dict(type='str', choices=['EXCLUDE', 'INCLUDE']),
                                        timed_metadata_id3_frame=dict(type='str', choices=['NONE', 'PRIV', 'TDRL']),
                                        timed_metadata_id3_period=dict(type='int'),
                                        timestamp_delta_milliseconds=dict(type='int'),
                                        ts_file_mode=dict(type='str', choices=['SEGMENTED_FILES', 'SINGLE_FILE'])
                                    )
                                ),
                                media_package_group_settings=dict(
                                    type='dict',
                                    options=dict(
                                        destination=dict(
                                            type='dict',
                                            options=dict(
                                                destination_ref_id=dict(type='str')
                                            )
                                        )
                                    )
                                ),
                                ms_smooth_group_settings=dict(
                                    type='dict',
                                    options=dict(
                                        acquisition_point_id=dict(type='str'),
                                        audio_only_timecode_control=dict(type='str', choices=['PASSTHROUGH', 'USE_CONFIGURED_CLOCK']),
                                        certificate_mode=dict(type='str', choices=['SELF_SIGNED', 'VERIFY_AUTHENTICITY']),
                                        connection_retry_interval=dict(type='int'),
                                        destination=dict(
                                            type='dict',
                                            options=dict(
                                                destination_ref_id=dict(type='str')
                                            )
                                        ),
                                        event_id=dict(type='str'),
                                        event_id_mode=dict(type='str', choices=['NO_EVENT_ID', 'USE_CONFIGURED', 'USE_TIMESTAMP']),
                                        event_stop_behavior=dict(type='str', choices=['NONE', 'SEND_EOS']),
                                        filecache_duration=dict(type='int'),
                                        fragment_length=dict(type='int'),
                                        input_loss_action=dict(type='str', choices=['EMIT_OUTPUT', 'PAUSE_OUTPUT']),
                                        num_retries=dict(type='int'),
                                        restart_delay=dict(type='int'),
                                        segmentation_mode=dict(type='str', choices=['USE_INPUT_SEGMENTATION', 'USE_SEGMENT_DURATION']),
                                        send_delay_ms=dict(type='int'),
                                        sparse_track_type=dict(type='str', choices=['NONE', 'SCTE_35', 'SCTE_35_WITHOUT_SEGMENTATION']),
                                        stream_manifest_behavior=dict(type='str', choices=['DO_NOT_SEND', 'SEND']),
                                        timestamp_offset=dict(type='str'),
                                        timestamp_offset_mode=dict(type='str', choices=['USE_CONFIGURED_OFFSET', 'USE_EVENT_START_DATE'])
                                    )
                                ),
                                multiplex_group_settings=dict(type='dict'),
                                rtmp_group_settings=dict(
                                    type='dict',
                                    options=dict(
                                        ad_markers=dict(type='list', elements='str', choices=['ON_CUE_POINT_SCTE35']),
                                        AuthenticationScheme=dict(type='str', choices=['AKAMAI', 'COMMON']),
                                        CacheFullBehavior=dict(type='str', choices=['DISCONNECT_IMMEDIATELY', 'WAIT_FOR_SERVER']),
                                        CacheLength=dict(type='int'),
                                        CaptionData=dict(type='str', choices=['ALL', 'FIELD1_608', 'FIELD1_AND_FIELD2_608']),
                                        InputLossAction=dict(type='str', choices=['EMIT_OUTPUT', 'PAUSE_OUTPUT']),
                                        RestartDelay=dict(type='int'),
                                        IncludeFillerNalUnits=dict(type='str', choices=['AUTO', 'DROP', 'INCLUDE'])
                                    )
                                ),
                                udp_group_settings=dict(
                                    type='dict',
                                    options=dict(
                                        input_loss_action=dict(type='str', choices=['DROP_PROGRAM', 'DROP_TS', 'EMIT_PROGRAM']),
                                        timed_metadata_id3_frame=dict(type='str', choices=['NONE', 'PRIV', 'TDRL']),
                                        timed_metadata_id3_period=dict(type='int')
                                    )
                                ),
                                cmaf_ingest_group_settings=dict(
                                    type='dict',
                                    options=dict(
                                        destination=dict(
                                            type='dict',
                                            options=dict(
                                                destination_ref_id=dict(type='str')
                                            )
                                        ),
                                        nielsen_id3_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                        scte35_type=dict(type='str', choices=['NONE', 'SCTE_35_WITHOUT_SEGMENTATION']),
                                        segment_length=dict(type='int'),
                                        segment_length_units=dict(type='str', choices=['MILLISECONDS', 'SECONDS']),
                                        send_delay_ms=dict(type='int'),
                                        klv_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                        klv_name_modifier=dict(type='str'),
                                        nielsen_id3_name_modifier=dict(type='str'),
                                        scte35_name_modifier=dict(type='str'),
                                        id3_behavior=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        id3_name_modifier=dict(type='str'),
                                        caption_language_mappings=dict(
                                            type='list',
                                            elements='dict',
                                            options=dict(
                                                caption_channel=dict(type='int'),
                                                language_code=dict(type='str')
                                            )
                                        ),
                                        timed_metadata_id3_frame=dict(type='str', choices=['NONE', 'PRIV', 'TDRL']),
                                        timed_metadata_id3_period=dict(type='int'),
                                        timed_metadata_passthrough=dict(type='str', choices=['DISABLED', 'ENABLED'])
                                    )
                                ),
                                srt_group_settings=dict(
                                    type='dict',
                                    options=dict(
                                        input_loss_action=dict(type='str', choices=['DROP_PROGRAM', 'DROP_TS', 'EMIT_PROGRAM'])
                                    )
                                )
                            )
                        ),
                        outputs=dict(
                            type='list',
                            elements='dict',
                            options=dict(
                                audio_description_names=dict(type='list', elements='str'),
                                caption_description_names=dict(type='list', elements='str'),
                                output_name=dict(type='str'),
                                output_settings=dict(
                                    type='dict',
                                    options=dict(
                                        archive_output_settings=dict(
                                            type='dict',
                                            options=dict(
                                                container_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        m2ts_settings=dict(
                                                            type='dict',
                                                            options=dict(
                                                                absent_input_audio_behavior=dict(type='str', choices=['DROP', 'ENCODE_SILENCE']),
                                                                arib=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                                                arib_captions_pid=dict(type='str'),
                                                                arib_captions_pid_control=dict(type='str', choices=['AUTO', 'USE_CONFIGURED']),
                                                                audio_buffer_model=dict(type='str', choices=['ATSC', 'DVB']),
                                                                audio_frames_per_pes=dict(type='int'),
                                                                audio_pids=dict(type='str'),
                                                                audio_stream_type=dict(type='str', choices=['ATSC', 'DVB']),
                                                                bitrate=dict(type='int'),
                                                                buffer_model=dict(type='str', choices=['MULTIPLEX', 'NONE']),
                                                                cc_descriptor=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                                                dvb_nit_settings=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        network_id=dict(type='int'),
                                                                        network_name=dict(type='str'),
                                                                        rep_interval=dict(type='int')
                                                                    )
                                                                ),
                                                                dvb_sdt_settings=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        output_sdt=dict(type='str', choices=['SDT_FOLLOW', 'SDT_FOLLOW_IF_PRESENT', 'SDT_MANUAL', 'SDT_NONE']),
                                                                        rep_interval=dict(type='int'),
                                                                        service_name=dict(type='str'),
                                                                        service_provider_name=dict(type='str')
                                                                    )
                                                                ),
                                                                dvb_sub_pids=dict(type='str'),
                                                                dvb_tdt_settings=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        rep_interval=dict(type='int')
                                                                    )
                                                                ),
                                                                dvb_teletext_pid=dict(type='str'),
                                                                ebif=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                ebp_audio_interval=dict(type='str', choices=['VIDEO_AND_FIXED_INTERVALS', 'VIDEO_INTERVAL']),
                                                                ebp_lookahead_ms=dict(type='int'),
                                                                ebp_placement=dict(type='str', choices=['VIDEO_AND_AUDIO_PIDS', 'VIDEO_PID']),
                                                                ecm_pid=dict(type='str'),
                                                                es_rate_in_pes=dict(type='str', choices=['EXCLUDE', 'INCLUDE']),
                                                                etv_platform_pid=dict(type='str'),
                                                                etv_signal_pid=dict(type='str'),
                                                                fragment_time=dict(type='float'),
                                                                klv=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                klv_data_pids=dict(type='str'),
                                                                nielsen_id3_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                null_packet_bitrate=dict(type='float'),
                                                                pat_interval=dict(type='int'),
                                                                pcr_control=dict(type='str', choices=['CONFIGURED_PCR_PERIOD', 'PCR_EVERY_PES_PACKET']),
                                                                pat_period=dict(type='int'),
                                                                pcr_pid=dict(type='str'),
                                                                pmt_interval=dict(type='int'),
                                                                pmt_pid=dict(type='str'),
                                                                program_num=dict(type='int'),
                                                                rate_mode=dict(type='str', choices=['CBR', 'VBR']),
                                                                scte27_pids=dict(type='str'),
                                                                scte35_control=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                scte35_pid=dict(type='str'),
                                                                segmentation_markers=dict(type='str', choices=['EBP', 'EBP_LEGACY', 'NONE', 'PSI_SEGSTART', 'RAI_ADAPT', 'RAI_SEGSTART']),
                                                                segmentation_style=dict(type='str', choices=['MAINTAIN_CADENCE', 'RESET_CADENCE']),
                                                                segmentation_time=dict(type='float'),
                                                                timed_metadata_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                timed_metadata_pid=dict(type='str'),
                                                                transport_stream_id=dict(type='int'),
                                                                video_pid=dict(type='str'),
                                                                scte35_preroll_pullup_milliseconds=dict(type='float')
                                                            )
                                                        ),
                                                        raw_settings=dict(type='dict')
                                                    )
                                                ),
                                                extension=dict(type='str'),
                                                name_modifier=dict(type='str')
                                            )
                                        ),
                                        frame_capture_output_settings=dict(
                                            type='dict',
                                            options=dict(
                                                name_modifier=dict(type='str')
                                            )
                                        ),
                                        hls_output_settings=dict(
                                            type='dict',
                                            options=dict(
                                                h265_packaging_type=dict(type='str', choices=['HEV1', 'HVC1']),
                                                hls_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        audio_only_hls_settings=dict(
                                                            type='dict',
                                                            options=dict(
                                                                audio_group_id=dict(type='str'),
                                                                audio_only_image=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        password_param=dict(type='str'),
                                                                        uri=dict(type='str'),
                                                                        username=dict(type='str')
                                                                    )
                                                                ),
                                                                audio_track_type=dict(
                                                                    type='str',
                                                                    choices=[
                                                                        'ALTERNATE_AUDIO_AUTO_SELECT',
                                                                        'ALTERNATE_AUDIO_AUTO_SELECT_DEFAULT',
                                                                        'ALTERNATE_AUDIO_NOT_AUTO_SELECT',
                                                                        'AUDIO_ONLY_VARIANT_STREAM',
                                                                    ]
                                                                ),
                                                                segment_type=dict(type='str', choices=['AAC', 'FMP4'])
                                                            )
                                                        ),
                                                        fmp4_hls_settings=dict(
                                                            type='dict',
                                                            options=dict(
                                                                audio_rendition_sets=dict(type='str'),
                                                                nielsen_id3_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                timed_metadata_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH'])
                                                            )
                                                        ),
                                                        frame_capture_hls_settings=dict(type='dict'),
                                                        standard_hls_settings=dict(
                                                            type='dict',
                                                            options=dict(
                                                                audio_rendition_sets=dict(type='str'),
                                                                m3u8_settings=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        audio_frames_per_pes=dict(type='int'),
                                                                        audio_pids=dict(type='str'),
                                                                        ecm_pid=dict(type='str'),
                                                                        nielsen_id3_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                        pat_interval=dict(type='int'),
                                                                        pcr_control=dict(type='str', choices=['CONFIGURED_PCR_PERIOD', 'PCR_EVERY_PES_PACKET']),
                                                                        pcr_period=dict(type='int'),
                                                                        pcr_pid=dict(type='str'),
                                                                        pmt_interval=dict(type='int'),
                                                                        pmt_pid=dict(type='str'),
                                                                        program_num=dict(type='int'),
                                                                        scte35_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                        scte35_pid=dict(type='str'),
                                                                        timed_metadata_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                        timed_metadata_pid=dict(type='str'),
                                                                        transport_stream_id=dict(type='int'),
                                                                        video_pid=dict(type='str'),
                                                                        klv_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                        klv_data_pids=dict(type='str')
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ),
                                                name_modifier=dict(type='str'),
                                                segment_modifier=dict(type='str')
                                            )
                                        ),
                                        media_package_output_settings=dict(type='dict'),
                                        ms_smooth_output_settings=dict(
                                            type='dict',
                                            options=dict(
                                                h265_packaging_type=dict(type='str', choices=['HEV1', 'HVC1']),
                                                name_modifier=dict(type='str')
                                            )
                                        ),
                                        multiplex_output_settings=dict(
                                            type='dict',
                                            options=dict(
                                                destination=dict(
                                                    type='dict',
                                                    options=dict(
                                                        destination_ref_id=dict(type='str')
                                                    )
                                                ),
                                                container_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        multiplex_m2ts_settings=dict(
                                                            type='dict',
                                                            options=dict(
                                                                absent_input_audio_behavior=dict(type='str', choices=['DROP', 'ENCODE_SILENCE']),
                                                                arib=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                                                audio_buffer_model=dict(type='str', choices=['ATSC', 'DVB']),
                                                                audio_frames_per_pes=dict(type='int'),
                                                                audio_stream_type=dict(type='str', choices=['ATSC', 'DVB']),
                                                                cc_descriptor=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                                                ebif=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                es_rate_in_pes=dict(type='str', choices=['EXCLUDE', 'INCLUDE']),
                                                                klv=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                nielsen_id3_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                pcr_control=dict(type='str', choices=['CONFIGURED_PCR_PERIOD', 'PCR_EVERY_PES_PACKET']),
                                                                pcr_period=dict(type='int'),
                                                                scte35_control=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                scte35_preroll_pullup_milliseconds=dict(type='float')
                                                            )
                                                        )
                                                    )
                                                )
                                            )
                                        ),
                                        rtmp_output_settings=dict(
                                            type='dict',
                                            options=dict(
                                                certificate_mode=dict(type='str', choices=['SELF_SIGNED', 'VERIFY_AUTHENTICITY']),
                                                connection_retry_interval=dict(type='int'),
                                                destination=dict(
                                                    type='dict',
                                                    options=dict(
                                                        destination_ref_id=dict(type='str')
                                                    )
                                                ),
                                                num_retries=dict(type='int')
                                            )
                                        ),
                                        udp_output_settings=dict(
                                            type='dict',
                                            options=dict(
                                                buffer_msec=dict(type='int'),
                                                container_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        m2ts_settings=dict(
                                                            type='dict',
                                                            options=dict(
                                                                absent_input_audio_behavior=dict(type='str', choices=['DROP', 'ENCODE_SILENCE']),
                                                                arib=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                                                arib_captions_pid=dict(type='str'),
                                                                arib_captions_pid_control=dict(type='str', choices=['AUTO', 'USE_CONFIGURED']),
                                                                audio_buffer_model=dict(type='str', choices=['ATSC', 'DVB']),
                                                                audio_frames_per_pes=dict(type='int'),
                                                                audio_pids=dict(type='str'),
                                                                audio_stream_type=dict(type='str', choices=['ATSC', 'DVB']),
                                                                bitrate=dict(type='int'),
                                                                buffer_model=dict(type='str', choices=['MULTIPLEX', 'NONE']),
                                                                cc_descriptor=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                                                dvb_nit_settings=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        network_id=dict(type='int'),
                                                                        network_name=dict(type='str'),
                                                                        rep_interval=dict(type='int')
                                                                    )
                                                                ),
                                                                dvb_sdt_settings=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        output_sdt=dict(type='str', choices=['SDT_FOLLOW', 'SDT_FOLLOW_IF_PRESENT', 'SDT_MANUAL', 'SDT_NONE']),
                                                                        rep_interval=dict(type='int'),
                                                                        service_name=dict(type='str'),
                                                                        service_provider_name=dict(type='str')
                                                                    )
                                                                ),
                                                                dvb_sub_pids=dict(type='str'),
                                                                dvb_tdt_settings=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        rep_interval=dict(type='int')
                                                                    )
                                                                ),
                                                                dvb_teletext_pid=dict(type='str'),
                                                                ebif=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                ebp_audio_interval=dict(type='str', choices=['VIDEO_AND_FIXED_INTERVALS', 'VIDEO_INTERVAL']),
                                                                ebp_lookahead_ms=dict(type='int'),
                                                                ebp_placement=dict(type='str', choices=['VIDEO_AND_AUDIO_PIDS', 'VIDEO_PID']),
                                                                ecm_pid=dict(type='str'),
                                                                es_rate_in_pes=dict(type='str', choices=['EXCLUDE', 'INCLUDE']),
                                                                etv_platform_pid=dict(type='str'),
                                                                etv_signal_pid=dict(type='str'),
                                                                fragment_time=dict(type='float'),
                                                                klv=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                klv_data_pids=dict(type='str'),
                                                                nielsen_id3_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                null_packet_bitrate=dict(type='float'),
                                                                pat_interval=dict(type='int'),
                                                                pcr_control=dict(type='str', choices=['CONFIGURED_PCR_PERIOD', 'PCR_EVERY_PES_PACKET']),
                                                                pcr_period=dict(type='int'),
                                                                pcr_pid=dict(type='str'),
                                                                pmt_interval=dict(type='int'),
                                                                pmt_pid=dict(type='str'),
                                                                program_num=dict(type='int'),
                                                                rate_mode=dict(type='str', choices=['CBR', 'VBR']),
                                                                scte27_pids=dict(type='str'),
                                                                scte35_control=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                scte35_pid=dict(type='str'),
                                                                segmentation_markers=dict(type='str', choices=['EBP', 'EBP_LEGACY', 'NONE', 'PSI_SEGSTART', 'RAI_ADAPT', 'RAI_SEGSTART']),
                                                                segmentation_style=dict(type='str', choices=['MAINTAIN_CADENCE', 'RESET_CADENCE']),
                                                                segmentation_time=dict(type='float'),
                                                                timed_metadata_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                timed_metadata_pid=dict(type='str'),
                                                                transport_stream_id=dict(type='int'),
                                                                video_pid=dict(type='str'),
                                                                scte35_preroll_pullup_milliseconds=dict(type='float')
                                                            )
                                                        )
                                                    )
                                                ),
                                                destination=dict(
                                                    type='dict',
                                                    options=dict(
                                                        destination_ref_id=dict(type='str')
                                                    )
                                                ),
                                                fec_output_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        column_depth=dict(type='int'),
                                                        include_fec=dict(type='str', choices=['COLUMN', 'COLUMN_AND_ROW']),
                                                        row_length=dict(type='int')
                                                    )
                                                )
                                            )
                                        ),
                                        cmaf_ingest_output_settings=dict(
                                            type='dict',
                                            options=dict(
                                                name_modifier=dict(type='str')
                                            )
                                        ),
                                        srt_output_settings=dict(
                                            type='dict',
                                            options=dict(
                                                buffer_msec=dict(type='int'),
                                                container_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        m2ts_settings=dict(
                                                            type='dict',
                                                            options=dict(
                                                                absent_input_audio_behavior=dict(type='str', choices=['DROP', 'ENCODE_SILENCE']),
                                                                arib=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                                                arib_captions_pid=dict(type='str'),
                                                                arib_captions_pid_control=dict(type='str', choices=['AUTO', 'USE_CONFIGURED']),
                                                                audio_buffer_model=dict(type='str', choices=['ATSC', 'DVB']),
                                                                audio_frames_per_pes=dict(type='int'),
                                                                audio_pids=dict(type='str'),
                                                                audio_stream_type=dict(type='str', choices=['ATSC', 'DVB']),
                                                                bitrate=dict(type='int'),
                                                                buffer_model=dict(type='str', choices=['MULTIPLEX', 'NONE']),
                                                                cc_descriptor=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                                                dvb_nit_settings=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        network_id=dict(type='int'),
                                                                        network_name=dict(type='str'),
                                                                        rep_interval=dict(type='int')
                                                                    )
                                                                ),
                                                                dvb_sdt_settings=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        output_sdt=dict(type='str', choices=['SDT_FOLLOW', 'SDT_FOLLOW_IF_PRESENT', 'SDT_MANUAL', 'SDT_NONE']),
                                                                        rep_interval=dict(type='int'),
                                                                        service_name=dict(type='str'),
                                                                        service_provider_name=dict(type='str')
                                                                    )
                                                                ),
                                                                dvb_sub_pids=dict(type='str'),
                                                                dvb_tdt_settings=dict(
                                                                    type='dict',
                                                                    options=dict(
                                                                        rep_interval=dict(type='int')
                                                                    )
                                                                ),
                                                                dvb_teletext_pid=dict(type='str'),
                                                                ebif=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                ebp_audio_interval=dict(type='str', choices=['VIDEO_AND_FIXED_INTERVALS', 'VIDEO_INTERVAL']),
                                                                ebp_lookahead_ms=dict(type='int'),
                                                                ebp_placement=dict(type='str', choices=['VIDEO_AND_AUDIO_PIDS', 'VIDEO_PID']),
                                                                ecm_pid=dict(type='str'),
                                                                es_rate_in_pes=dict(type='str', choices=['EXCLUDE', 'INCLUDE']),
                                                                etv_platform_pid=dict(type='str'),
                                                                etv_signal_pid=dict(type='str'),
                                                                fragment_time=dict(type='float'),
                                                                klv=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                klv_data_pids=dict(type='str'),
                                                                nielsen_id3_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                null_packet_bitrate=dict(type='float'),
                                                                pat_interval=dict(type='int'),
                                                                pcr_control=dict(type='str', choices=['CONFIGURED_PCR_PERIOD', 'PCR_EVERY_PES_PACKET']),
                                                                pcr_period=dict(type='int'),
                                                                pcr_pid=dict(type='str'),
                                                                pmt_interval=dict(type='int'),
                                                                pmt_pid=dict(type='str'),
                                                                program_num=dict(type='int'),
                                                                rate_mode=dict(type='str', choices=['CBR', 'VBR']),
                                                                scte27_pids=dict(type='str'),
                                                                scte35_control=dict(type='str', choices=['NONE', 'PASSTHROUGH']),
                                                                scte35_pid=dict(type='str'),
                                                                segmentation_markers=dict(type='str', choices=['EBP', 'EBP_LEGACY', 'NONE', 'PSI_SEGSTART', 'RAI_ADAPT', 'RAI_SEGSTART']),
                                                                segmentation_style=dict(type='str', choices=['MAINTAIN_CADENCE', 'RESET_CADENCE']),
                                                                segmentation_time=dict(type='float'),
                                                                timed_metadata_behavior=dict(type='str', choices=['NO_PASSTHROUGH', 'PASSTHROUGH']),
                                                                timed_metadata_pid=dict(type='str'),
                                                                transport_stream_id=dict(type='int'),
                                                                video_pid=dict(type='str'),
                                                                scte35_preroll_pullup_milliseconds=dict(type='float')
                                                            )
                                                        )
                                                    )
                                                ),
                                                destination = dict(
                                                    type='dict',
                                                    options=dict(
                                                        destination_ref_id=dict(type='str')
                                                    )
                                                ),
                                                encryption_type = dict(type='str', choices=['AES128', 'AES192', 'AES256']),
                                                latency = dict(type='int')
                                            )
                                        )
                                    )
                                ),
                                video_description_name=dict(type='str')
                            )
                        )
                    )
                ),
                timecode_config=dict(
                    type='dict',
                    options=dict(
                        source=dict(type='str', choices=['EMBEDDED', 'SYSTEMCLOCK', 'ZEROBASED']),
                        sync_threshold=dict(type='int')
                    )
                ),
                video_descriptions=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        codec_settings=dict(
                            type='dict',
                            options=dict(
                                frame_capture_settings=dict(
                                    type='dict',
                                    options=dict(
                                        capture_interval=dict(type='int'),
                                        capture_interval_units=dict(type='str', choices=['MILLISECONDS', 'SECONDS']),
                                        timecode_burnin_settings=dict(
                                            type='dict',
                                            options=dict(
                                                font_size=dict(type='str', choices=['EXTRA_SMALL_10', 'LARGE_48', 'MEDIUM_32', 'SMALL_16']),
                                                position=dict(
                                                    type='str',
                                                    choices=[
                                                        'BOTTOM_CENTER',
                                                        'BOTTOM_LEFT',
                                                        'BOTTOM_RIGHT',
                                                        'MIDDLE_CENTER',
                                                        'MIDDLE_LEFT',
                                                        'MIDDLE_RIGHT',
                                                        'TOP_CENTER',
                                                        'TOP_LEFT',
                                                        'TOP_RIGHT',
                                                    ]
                                                ),
                                                prefix=dict(type='str')
                                            )
                                        )
                                    )
                                ),
                                h264_settings=dict(
                                    type='dict',
                                    options=dict(
                                        adaptive_quantization=dict(type='str', choices=['AUTO', 'HIGH', 'HIGHER', 'LOW', 'MAX', 'MEDIUM', 'OFF']),
                                        afd_signaling=dict(type='str', choices=['AUTO', 'FIXED', 'NONE']),
                                        bitrate=dict(type='int'),
                                        buf_fill_pct=dict(type='int'),
                                        buf_size=dict(type='int'),
                                        color_metadata=dict(type='str', choices=['IGNORE', 'INSERT']),
                                        color_space_settings=dict(
                                            type='dict',
                                            options=dict(
                                                color_space_passthrough_settings=dict(type='dict'),
                                                rec601_settings=dict(type='dict'),
                                                rec709_settings=dict(type='dict')
                                            )
                                        ),
                                        entropy_encoding=dict(type='str', choices=['CABAC', 'CAVLC']),
                                        filter_settings=dict(
                                            type='dict',
                                            options=dict(
                                                temporal_filter_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        post_filter_sharpening=dict(type='str', choices=['AUTO', 'DISABLED', 'ENABLED']),
                                                        strength=dict(
                                                            type='str',
                                                            choices=[
                                                                'AUTO',
                                                                'STRENGTH_1',
                                                                'STRENGTH_2',
                                                                'STRENGTH_3',
                                                                'STRENGTH_4',
                                                                'STRENGTH_5',
                                                                'STRENGTH_6',
                                                                'STRENGTH_7',
                                                                'STRENGTH_8',
                                                                'STRENGTH_9',
                                                                'STRENGTH_10',
                                                                'STRENGTH_11',
                                                                'STRENGTH_12',
                                                                'STRENGTH_13',
                                                                'STRENGTH_14',
                                                                'STRENGTH_15',
                                                                'STRENGTH_16',
                                                            ]
                                                        )
                                                    )
                                                ),
                                                bandwidth_reduction_filter_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        post_filter_sharpening=dict(type='str', choices=['DISABLED', 'SHARPENING_1', 'SHARPENING_2', 'SHARPENING_3']),
                                                        strength=dict(type='str', choices=['AUTO', 'STRENGTH_1', 'STRENGTH_2', 'STRENGTH_3', 'STRENGTH_4'])
                                                    )
                                                )
                                            )
                                        ),
                                        fixed_afd=dict(
                                            type='str',
                                            choices=[
                                                'AFD_0000',
                                                'AFD_0010',
                                                'AFD_0011',
                                                'AFD_0100',
                                                'AFD_1000',
                                                'AFD_1001',
                                                'AFD_1010',
                                                'AFD_1011',
                                                'AFD_1101',
                                                'AFD_1110',
                                                'AFD_1111',
                                            ]
                                        ),
                                        flicker_aq=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        force_field_pictures=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        framerate_control=dict(type='str', choices=['INITIALIZE_FROM_SOURCE', 'SPECIFIED']),
                                        framerate_denominator=dict(type='int'),
                                        framerate_numerator=dict(type='int'),
                                        gop_b_reference=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        gop_closed_cadence=dict(type='int'),
                                        gop_num_b_frames=dict(type='int'),
                                        gop_size=dict(type='float'),
                                        gop_size_units=dict(type='str', choices=['FRAMES', 'SECONDS']),
                                        level=dict(
                                            type='str',
                                            choices=[
                                                'H264_LEVEL_1',
                                                'H264_LEVEL_1_1',
                                                'H264_LEVEL_1_2',
                                                'H264_LEVEL_1_3',
                                                'H264_LEVEL_2',
                                                'H264_LEVEL_2_1',
                                                'H264_LEVEL_2_2',
                                                'H264_LEVEL_3',
                                                'H264_LEVEL_3_1',
                                                'H264_LEVEL_3_2',
                                                'H264_LEVEL_4',
                                                'H264_LEVEL_4_1',
                                                'H264_LEVEL_4_2',
                                                'H264_LEVEL_5',
                                                'H264_LEVEL_5_1',
                                                'H264_LEVEL_5_2',
                                                'H264_LEVEL_AUTO',
                                            ]
                                        ),
                                        look_ahead_rate_control=dict(type='str', choices=['HIGH', 'LOW', 'MEDIUM']),
                                        max_bitrate=dict(type='int'),
                                        min_i_interval=dict(type='int'),
                                        num_ref_frames=dict(type='int'),
                                        par_control=dict(type='str', choices=['INITIALIZE_FROM_SOURCE', 'SPECIFIED']),
                                        par_denominator=dict(type='int'),
                                        par_numerator=dict(type='int'),
                                        profile=dict(type='str', choices=['BASELINE', 'HIGH', 'HIGH_10BIT', 'HIGH_422', 'HIGH_422_10BIT', 'MAIN']),
                                        quality_level=dict(type='str', choices=['ENHANCED_QUALITY', 'STANDARD_QUALITY']),
                                        qvbr_quality_level=dict(type='int'),
                                        rate_control_mode=dict(type='str', choices=['CBR', 'MULTIPLEX', 'QVBR', 'VBR']),
                                        scan_type=dict(type='str', choices=['INTERLACED', 'PROGRESSIVE']),
                                        scene_change_detect=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        slices=dict(type='int'),
                                        softness=dict(type='int'),
                                        spatial_aq=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        subgop_length=dict(type='str', choices=['DYNAMIC', 'FIXED']),
                                        syntax=dict(type='str', choices=['DEFAULT', 'RP2027']),
                                        temporal_aq=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        timecode_insertion=dict(type='str', choices=['DISABLED', 'PIC_TIMING_SEI']),
                                        timecode_burnin_settings=dict(
                                            type='dict',
                                            options=dict(
                                                font_size=dict(type='str', choices=['EXTRA_SMALL_10', 'LARGE_48', 'MEDIUM_32', 'SMALL_16']),
                                                position=dict(
                                                    type='str',
                                                    choices=[
                                                        'BOTTOM_CENTER',
                                                        'BOTTOM_LEFT',
                                                        'BOTTOM_RIGHT',
                                                        'MIDDLE_CENTER',
                                                        'MIDDLE_LEFT',
                                                        'MIDDLE_RIGHT',
                                                        'TOP_CENTER',
                                                        'TOP_LEFT',
                                                        'TOP_RIGHT',
                                                    ]
                                                ),
                                                prefix=dict(type='str')
                                            )
                                        ),
                                        min_qp=dict(type='int')
                                    )
                                ),
                                h265_settings=dict(
                                    type='dict',
                                    options=dict(
                                        adaptive_quantization=dict(type='str', choices=['AUTO', 'HIGH', 'HIGHER', 'LOW', 'MAX', 'MEDIUM', 'OFF']),
                                        afd_signaling=dict(type='str', choices=['AUTO', 'FIXED', 'NONE']),
                                        alternative_transfer_function=dict(type='str', choices=['INSERT', 'OMIT']),
                                        bitrate=dict(type='int'),
                                        buf_size=dict(type='int'),
                                        color_metadata=dict(type='str', choices=['IGNORE', 'INSERT']),
                                        color_space_settings=dict(
                                            type='dict',
                                            options=dict(
                                                color_space_passthrough_settings=dict(type='dict'),
                                                dolby_vision81_settings=dict(type='dict'),
                                                hdr10_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        max_cll=dict(type='int'),
                                                        max_fall=dict(type='int')
                                                    )
                                                ),
                                                rec601_settings=dict(type='dict'),
                                                rec709_settings=dict(type='dict')
                                            )
                                        ),
                                        filter_settings=dict(
                                            type='dict',
                                            options=dict(
                                                temporal_filter_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        post_filter_sharpening=dict(type='str', choices=['AUTO', 'DISABLED', 'ENABLED']),
                                                        strength=dict(
                                                            type='str',
                                                            choices=[
                                                                'AUTO',
                                                                'STRENGTH_1',
                                                                'STRENGTH_2',
                                                                'STRENGTH_3',
                                                                'STRENGTH_4',
                                                                'STRENGTH_5',
                                                                'STRENGTH_6',
                                                                'STRENGTH_7',
                                                                'STRENGTH_8',
                                                                'STRENGTH_9',
                                                                'STRENGTH_10',
                                                                'STRENGTH_11',
                                                                'STRENGTH_12',
                                                                'STRENGTH_13',
                                                                'STRENGTH_14',
                                                                'STRENGTH_15',
                                                                'STRENGTH_16',
                                                            ]
                                                        )
                                                    )
                                                ),
                                                bandwidth_reduction_filter_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        post_filter_sharpening=dict(type='str', choices=['DISABLED', 'SHARPENING_1', 'SHARPENING_2', 'SHARPENING_3']),
                                                        strength=dict(type='str', choices=['AUTO', 'STRENGTH_1', 'STRENGTH_2', 'STRENGTH_3', 'STRENGTH_4'])
                                                    )
                                                )
                                            )
                                        ),
                                        fixed_afd=dict(
                                            type='str',
                                            choices=[
                                                'AFD_0000',
                                                'AFD_0010',
                                                'AFD_0011',
                                                'AFD_0100',
                                                'AFD_1000',
                                                'AFD_1001',
                                                'AFD_1010',
                                                'AFD_1011',
                                                'AFD_1101',
                                                'AFD_1110',
                                                'AFD_1111',
                                            ]
                                        ),
                                        flicker_aq=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        framerate_denominator=dict(type='int'),
                                        framerate_numerator=dict(type='int'),
                                        gop_closed_cadence=dict(type='int'),
                                        gop_size=dict(type='float'),
                                        gop_size_units=dict(type='str', choices=['FRAMES', 'SECONDS']),
                                        level=dict(
                                            type='str',
                                            choices=[
                                                'H265_LEVEL_1',
                                                'H265_LEVEL_2',
                                                'H265_LEVEL_2_1',
                                                'H265_LEVEL_3',
                                                'H265_LEVEL_3_1',
                                                'H265_LEVEL_4',
                                                'H265_LEVEL_4_1',
                                                'H265_LEVEL_5',
                                                'H265_LEVEL_5_1',
                                                'H265_LEVEL_5_2',
                                                'H265_LEVEL_6',
                                                'H265_LEVEL_6_1',
                                                'H265_LEVEL_6_2',
                                                'H265_LEVEL_AUTO',
                                            ]
                                        ),
                                        look_ahead_rate_control=dict(type='str', choices=['HIGH', 'LOW', 'MEDIUM']),
                                        max_bitrate=dict(type='int'),
                                        min_i_interval=dict(type='int'),
                                        par_denominator=dict(type='int'),
                                        par_numerator=dict(type='int'),
                                        profile=dict(type='str', choices=['MAIN', 'MAIN_10BIT']),
                                        qvbr_quality_level=dict(type='int'),
                                        rate_control_mode=dict(type='str', choices=['CBR', 'MULTIPLEX', 'QVBR']),
                                        scan_type=dict(type='str', choices=['INTERLACED', 'PROGRESSIVE']),
                                        scene_change_detect=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        slices=dict(type='int'),
                                        tier=dict(type='str', choices=['HIGH', 'MAIN']),
                                        timecode_insertion=dict(type='str', choices=['DISABLED', 'PIC_TIMING_SEI']),
                                        timecode_burnin_settings=dict(
                                            type='dict',
                                            options=dict(
                                                font_size=dict(type='str', choices=['EXTRA_SMALL_10', 'LARGE_48', 'MEDIUM_32', 'SMALL_16']),
                                                position=dict(
                                                    type='str',
                                                    choices=[
                                                        'BOTTOM_CENTER',
                                                        'BOTTOM_LEFT',
                                                        'BOTTOM_RIGHT',
                                                        'MIDDLE_CENTER',
                                                        'MIDDLE_LEFT',
                                                        'MIDDLE_RIGHT',
                                                        'TOP_CENTER',
                                                        'TOP_LEFT',
                                                        'TOP_RIGHT',
                                                    ]
                                                ),
                                                prefix=dict(type='str')
                                            )
                                        ),
                                        mv_over_picture_boundaries=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        mv_temporal_predictor=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        tile_height=dict(type='int'),
                                        tile_padding=dict(type='str', choices=['NONE', 'PADDED']),
                                        tile_width=dict(type='int'),
                                        treeblock_size=dict(type='str', choices=['AUTO', 'TREE_SIZE_32X32']),
                                        min_qp=dict(type='int'),
                                        deblocking=dict(type='str', choices=['DISABLED', 'ENABLED'])
                                    )
                                ),
                                mpeg2_settings=dict(
                                    type='dict',
                                    options=dict(
                                        adaptive_quantization=dict(type='str', choices=['AUTO', 'HIGH', 'LOW', 'MEDIUM', 'OFF']),
                                        afd_signaling=dict(type='str', choices=['AUTO', 'FIXED', 'NONE']),
                                        color_metadata=dict(type='str', choices=['IGNORE', 'INSERT']),
                                        color_space=dict(type='str', choices=['AUTO', 'PASSTHROUGH']),
                                        display_aspect_ratio=dict(type='str', choices=['DISPLAYRATIO16X9', 'DISPLAYRATIO4X3']),
                                        filter_settings=dict(
                                            type='dict',
                                            options=dict(
                                                temporal_filter_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        post_filter_sharpening=dict(type='str', choices=['AUTO', 'DISABLED', 'ENABLED']),
                                                        strength=dict(
                                                            type='str',
                                                            choices=[
                                                                'AUTO',
                                                                'STRENGTH_1',
                                                                'STRENGTH_2',
                                                                'STRENGTH_3',
                                                                'STRENGTH_4',
                                                                'STRENGTH_5',
                                                                'STRENGTH_6',
                                                                'STRENGTH_7',
                                                                'STRENGTH_8',
                                                                'STRENGTH_9',
                                                                'STRENGTH_10',
                                                                'STRENGTH_11',
                                                                'STRENGTH_12',
                                                                'STRENGTH_13',
                                                                'STRENGTH_14',
                                                                'STRENGTH_15',
                                                                'STRENGTH_16',
                                                            ]
                                                        )
                                                    )
                                                )
                                            )
                                        ),
                                        fixed_afd=dict(
                                            type='str',
                                            choices=[
                                                'AFD_0000',
                                                'AFD_0010',
                                                'AFD_0011',
                                                'AFD_0100',
                                                'AFD_1000',
                                                'AFD_1001',
                                                'AFD_1010',
                                                'AFD_1011',
                                                'AFD_1101',
                                                'AFD_1110',
                                                'AFD_1111',
                                            ]
                                        ),
                                        framerate_denominator=dict(type='int'),
                                        framerate_numerator=dict(type='int'),
                                        gop_closed_cadence=dict(type='int'),
                                        gop_num_b_frames=dict(type='int'),
                                        gop_size=dict(type='float'),
                                        gop_size_units=dict(type='str', choices=['FRAMES', 'SECONDS']),
                                        scan_type=dict(type='str', choices=['INTERLACED', 'PROGRESSIVE']),
                                        subgop_length=dict(type='str', choices=['DYNAMIC', 'FIXED']),
                                        timecode_insertion=dict(type='str', choices=['DISABLED', 'GOP_TIMECODE']),
                                        timecode_burnin_settings=dict(
                                            type='dict',
                                            options=dict(
                                                font_size=dict(type='str', choices=['EXTRA_SMALL_10', 'LARGE_48', 'MEDIUM_32', 'SMALL_16']),
                                                position=dict(
                                                    type='str',
                                                    choices=[
                                                        'BOTTOM_CENTER',
                                                        'BOTTOM_LEFT',
                                                        'BOTTOM_RIGHT',
                                                        'MIDDLE_CENTER',
                                                        'MIDDLE_LEFT',
                                                        'MIDDLE_RIGHT',
                                                        'TOP_CENTER',
                                                        'TOP_LEFT',
                                                        'TOP_RIGHT',
                                                    ]
                                                ),
                                                prefix=dict(type='str')
                                            )
                                        )
                                    )
                                ),
                                av1_settings=dict(
                                    type='dict',
                                    options=dict(
                                        afd_signaling=dict(type='str', choices=['AUTO', 'FIXED', 'NONE']),
                                        buf_size=dict(type='int'),
                                        color_space_settings=dict(
                                            type='dict',
                                            options=dict(
                                                color_space_passthrough_settings=dict(type='dict'),
                                                hdr10_settings=dict(
                                                    type='dict',
                                                    options=dict(
                                                        
                                                        max_cll=dict(type='int'),
                                                        max_fall=dict(type='int')
                                                    )
                                                ),
                                                rec601_settings=dict(type='dict'),
                                                rec709_settings=dict(type='dict')
                                            )
                                        ),
                                        fixed_afd=dict(
                                            type='str',
                                            choices=[
                                                'AFD_0000',
                                                'AFD_0010',
                                                'AFD_0011',
                                                'AFD_0100',
                                                'AFD_1000',
                                                'AFD_1001',
                                                'AFD_1010',
                                                'AFD_1011',
                                                'AFD_1101',
                                                'AFD_1110',
                                                'AFD_1111',
                                            ]
                                        ),
                                        framerate_denominator=dict(type='int'),
                                        framerate_numerator=dict(type='int'),
                                        gop_size=dict(type='float'),
                                        gop_size_units=dict(type='str', choices=['FRAMES', 'SECONDS']),
                                        level=dict(
                                            type='str',
                                            choices=[
                                                'AV1_LEVEL_2',
                                                'AV1_LEVEL_2_1',
                                                'AV1_LEVEL_3',
                                                'AV1_LEVEL_3_1',
                                                'AV1_LEVEL_4',
                                                'AV1_LEVEL_4_1',
                                                'AV1_LEVEL_5',
                                                'AV1_LEVEL_5_1',
                                                'AV1_LEVEL_5_2',
                                                'AV1_LEVEL_5_3',
                                                'AV1_LEVEL_6',
                                                'AV1_LEVEL_6_1',
                                                'AV1_LEVEL_6_2',
                                                'AV1_LEVEL_6_3',
                                                'AV1_LEVEL_AUTO',
                                            ]
                                        ),
                                        look_ahead_rate_control=dict(type='str', choices=['HIGH', 'LOW', 'MEDIUM']),
                                        max_bitrate=dict(type='int'),
                                        min_i_interval=dict(type='int'),
                                        par_denominator=dict(type='int'),
                                        par_numerator=dict(type='int'),
                                        qvbr_quality_level=dict(type='int'),
                                        scene_change_detect=dict(type='str', choices=['DISABLED', 'ENABLED']),
                                        timecode_burnin_settings=dict(
                                            type='dict',
                                            options=dict(
                                                font_size=dict(type='str', choices=['EXTRA_SMALL_10', 'LARGE_48', 'MEDIUM_32', 'SMALL_16']),
                                                position=dict(
                                                    type='str',
                                                    choices=[
                                                        'BOTTOM_CENTER',
                                                        'BOTTOM_LEFT',
                                                        'BOTTOM_RIGHT',
                                                        'MIDDLE_CENTER',
                                                        'MIDDLE_LEFT',
                                                        'MIDDLE_RIGHT',
                                                        'TOP_CENTER',
                                                        'TOP_LEFT',
                                                        'TOP_RIGHT',
                                                    ]
                                                ),
                                                prefix=dict(type='str')
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        height=dict(type='int'),
                        name=dict(type='str'),
                        respond_to_afd=dict(type='str', choices=['NONE', 'PASSTHROUGH', 'RESPOND']),
                        scaling_behavior=dict(type='str', choices=['DEFAULT', 'STRETCH_TO_OUTPUT']),
                        sharpness=dict(type='int'),
                        width=dict(type='int')
                    )
                ),
                thumbnail_configuration=dict(
                    type='dict',
                    options=dict(
                        state=dict(type='str', choices=['AUTO', 'DISABLED'])
                    )
                ),
                color_correction_settings=dict(
                    type='dict',
                    options=dict(
                        global_color_corrections=dict(
                            type='list',
                            elements='dict',
                            options=dict(
                                input_color_space=dict(type='str', choices=['HDR10', 'HLG_2020', 'REC_601', 'REC_709']),
                                output_color_space=dict(type='str', choices=['HDR10', 'HLG_2020', 'REC_601', 'REC_709']),
                                uri=dict(type='str')
                            )
                        )
                    )
                )
            )
        ),
        input_attachments=dict(
            type='list',
            elements='dict',
            options=dict(
                automatic_input_failover_settings=dict(
                    type='dict',
                    options=dict(
                        error_clear_time_msec=dict(type='int'),
                        failover_conditions=dict(
                            type='list',
                            elements='dict',
                            options=dict(
                                failover_condition_settings=dict(
                                    type='dict',
                                    options=dict(
                                        audio_silence_settings=dict(
                                            type='dict',
                                            options=dict(
                                                audio_selector_name=dict(type='str'),
                                                audio_silence_threshold_msec=dict(type='int')
                                            )
                                        ),
                                        input_loss_settings=dict(
                                            type='dict',
                                            options=dict(
                                                input_loss_threshold_msec=dict(type='int')
                                            )
                                        ),
                                        video_black_settings=dict(
                                            type='dict',
                                            options=dict(
                                                black_detect_threshold=dict(type='float'),
                                                video_black_threshold_msec=dict(type='int')
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        input_preference=dict(type='str', choices=['EQUAL_INPUT_PREFERENCE', 'PRIMARY_INPUT_PREFERRED']),
                        secondary_input_id=dict(type='str')
                    )
                ),
                input_attachment_name=dict(type='str'),
                input_id=dict(type='str'),
                input_settings=dict(
                    type='dict',
                    options=dict(
                        audio_selectors=dict(
                            type='list',
                            elements='dict',
                            options=dict(
                                name=dict(type='str'),
                                selector_settings=dict(
                                    type='dict',
                                    options=dict(
                                        audio_hls_rendition_selection=dict(
                                            type='dict',
                                            options=dict(
                                                group_id=dict(type='str'),
                                                name=dict(type='str')
                                            )
                                        ),
                                        audio_language_selection=dict(
                                            type='dict',
                                            options=dict(
                                                language_code=dict(type='str'),
                                                language_selection_policy=dict(type='str', choices=['LOOSE', 'STRICT'])
                                            )
                                        ),
                                        audio_pid_selection=dict(
                                            type='dict',
                                            options=dict(
                                                pid=dict(type='int')
                                            )
                                        ),
                                        audio_track_selection=dict(
                                            type='dict',
                                            options=dict(
                                                tracks=dict(
                                                    type='list',
                                                    elements='dict',
                                                    options=dict(
                                                        track=dict(type='int')
                                                    )
                                                ),
                                                dolby_e_decode=dict(
                                                    type='dict',
                                                    options=dict(
                                                        program_selection=dict(
                                                            type='str',
                                                            choices=[
                                                                'ALL_CHANNELS',
                                                                'PROGRAM_1',
                                                                'PROGRAM_2',
                                                                'PROGRAM_3',
                                                                'PROGRAM_4',
                                                                'PROGRAM_5',
                                                                'PROGRAM_6',
                                                                'PROGRAM_7',
                                                                'PROGRAM_8'
                                                            ]
                                                        )
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        caption_selectors=dict(
                            type='list',
                            elements='dict',
                            options=dict(
                                language_code=dict(type='str'),
                                name=dict(type='str'),
                                selector_settings=dict(
                                    type='dict',
                                    options=dict(
                                        ancillary_source_settings=dict(
                                            type='dict',
                                            options=dict(
                                                source_ancillary_channel_number=dict(type='int')
                                            )
                                        ),
                                        arib_source_settings=dict(type='dict'),
                                        dvb_sub_source_settings=dict(
                                            type='dict',
                                            options=dict(
                                                ocr_language=dict(type='str', choices=['DEU', 'ENG', 'FRA', 'NLD', 'POR', 'SPA']),
                                                pid=dict(type='int')
                                            )
                                        ),
                                        embedded_source_settings=dict(
                                            type='dict',
                                            options=dict(
                                                convert608_to708=dict(type='str', choices=['DISABLED', 'UPCONVERT']),
                                                scte20_detection=dict(type='str', choices=['AUTO', 'OFF']),
                                                source608_channel_number=dict(type='int'),
                                                source608_track_number=dict(type='int')
                                            )
                                        ),
                                        scte20_source_settings=dict(
                                            type='dict',
                                            options=dict(
                                                convert608_to708=dict(type='str', choices=['DISABLED', 'UPCONVERT']),
                                                source608_channel_number=dict(type='int')
                                            )
                                        ),
                                        scte27_source_settings=dict(
                                            type='dict',
                                            options=dict(
                                                ocr_language=dict(type='str', choices=['DEU', 'ENG', 'FRA', 'NLD', 'POR', 'SPA']),
                                                pid=dict(type='int')
                                            )
                                        ),
                                        teletext_source_settings=dict(
                                            type='dict',
                                            options=dict(
                                                output_rectangle=dict(
                                                    type='dict',
                                                    options=dict(
                                                        height=dict(type='float'),
                                                        left_offset=dict(type='float'),
                                                        top_offset=dict(type='float'),
                                                        width=dict(type='float')
                                                    )
                                                ),
                                                page_number=dict(type='str')
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        deblock_filter=dict(type='str', choices=['DISABLED', 'ENABLED']),
                        denoise_filter=dict(type='str', choices=['DISABLED', 'ENABLED']),
                        filter_strength=dict(type='int'),
                        input_filter=dict(type='str', choices=['AUTO', 'DISABLED', 'FORCED']),
                        network_input_settings=dict(
                            type='dict',
                            options=dict(
                                hls_input_settings=dict(
                                    type='dict',
                                    options=dict(
                                        bandwidth=dict(type='int'),
                                        buffer_segments=dict(type='int'),
                                        retries=dict(type='int'),
                                        retry_interval=dict(type='int'),
                                        scte35_source=dict(type='str', choices=['MANIFEST', 'SEGMENTS'])
                                    )
                                ),
                                server_validation=dict(type='str', choices=['CHECK_CRYPTOGRAPHY_AND_VALIDATE_NAME', 'CHECK_CRYPTOGRAPHY_ONLY']),
                                multicast_input_settings=dict(
                                    type='dict',
                                    options=dict(
                                        source_ip_address=dict(type='str')
                                    )
                                )
                            )
                        ),
                        scte35_pid=dict(type='int'),
                        smpte2038_data_preference=dict(type='str', choices=['IGNORE', 'PREFER']),
                        source_end_behavior=dict(type='str', choices=['CONTINUE', 'LOOP']),
                        video_selector=dict(
                            type='dict',
                            options=dict(
                                color_space=dict(type='str', choices=['FOLLOW', 'HDR10', 'HLG_2020', 'REC_601', 'REC_709']),
                                color_space_settings=dict(
                                    type='dict',
                                    options=dict(
                                        hdr10_settings=dict(
                                            type='dict',
                                            options=dict(
                                                max_cll=dict(type='int'),
                                                max_fall=dict(type='int')
                                            )
                                        )
                                    )
                                ),
                                color_space_usage=dict(type='str', choices=['FALLBACK', 'FORCE']),
                                selector_settings=dict(
                                    type='dict',
                                    options=dict(
                                        video_selector_pid=dict(
                                            type='dict',
                                            options=dict(
                                                pid=dict(type='int')
                                            )
                                        ),
                                        video_selector_program_id=dict(
                                            type='dict',
                                            options=dict(
                                                program_id=dict(type='int')
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                ),
                logical_interface_names=dict(type='list', elements='str')
            )
        ),
        input_specification=dict(
            type='dict',
            options=dict(
                codec=dict(type='str', choices=['MPEG2', 'AVC', 'HEVC']),
                maximum_bitrate=dict(type='str', choices=['MAX_10_MBPS', 'MAX_20_MBPS', 'MAX_50_MBPS']),
                resolution=dict(type='str', choices=['SD', 'HD', 'UHD'])
            )
        ),
        log_level=dict(type='str', choices=['ERROR', 'WARNING', 'INFO', 'DEBUG', 'DISABLED']),
        maintenance=dict(
            type='dict',
            options=dict(
                maintenance_day=dict(type='str', choices=['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']),
                maintenance_start_time=dict(type='str')
            )
        ),
        reserved=dict(type='str'),
        role_arn=dict(type='str'),
        vpc=dict(
            type='dict',
            options=dict(
                public_address_allocation_ids=dict(type='list', elements='str'),
                security_group_ids=dict(type='list', elements='str'),
                subnet_ids=dict(type='list', elements='str')
            )
        ),
        anywhere_settings=dict(
            type='dict',
            options=dict(
                channel_placement_group_id=dict(type='str'),
                cluster_id=dict(type='str')
            )
        ),
        channel_engine_version=dict(
            type='dict',
            options=dict(
                version=dict(type='str')
            )
        ),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        dry_run=dict(type='bool'),
        tags=dict(type='dict'),
        purge_tags=dict(type='bool', default=True),
        wait=dict(type='bool', default=True),
        wait_timeout=dict(type='int', default=60),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('id', 'channel_id', 'name', 'channel_name')]
    )

    # Extract module parameters
    channel_id = get_arg('id', module.params, argument_spec)
    channel_name = get_arg('name', module.params, argument_spec)
    cdi_input_specification = get_arg('cdi_input_specification', module.params, argument_spec)
    channel_class = get_arg('channel_class', module.params, argument_spec)
    destinations = get_arg('destinations', module.params, argument_spec)
    encoder_settings = get_arg('encoder_settings', module.params, argument_spec)
    input_attachments = get_arg('input_attachments', module.params, argument_spec)
    input_specification = get_arg('input_specification', module.params, argument_spec)
    log_level = get_arg('log_level', module.params, argument_spec)
    maintenance = get_arg('maintenance', module.params, argument_spec)
    reserved = get_arg('reserved', module.params, argument_spec)
    role_arn = get_arg('role_arn', module.params, argument_spec)
    vpc = get_arg('vpc', module.params, argument_spec)
    anywhere_settings = get_arg('anywhere_settings', module.params, argument_spec)
    channel_engine_version = get_arg('channel_engine_version', module.params, argument_spec)
    dry_run = get_arg('dry_run', module.params, argument_spec)
    state = get_arg('state', module.params, argument_spec)
    wait = get_arg('wait', module.params, argument_spec)
    wait_timeout = get_arg('wait_timeout', module.params, argument_spec)
    tags = get_arg('tags', module.params, argument_spec)
    purge_tags = get_arg('purge_tags', module.params, argument_spec)

    # Initialize the manager
    manager = MediaLiveChannelManager(module)

    # Find the channel by ID or name
    if channel_id:
        manager.get_channel_by_id(channel_id)
    elif channel_name:
        manager.get_channel_by_name(channel_name)
        channel_id = manager.channel.get('channel_id')

    # Do nothing in check mode
    if module.check_mode:
        module.exit_json(changed=True)

    # Handle present state
    if state == 'present':

        # Case update
        if manager.channel:

            update_params = {
                'channel_id': channel_id,
                'name': channel_name,
                'cdi_input_specification': cdi_input_specification,
                'destinations': destinations,
                'encoder_settings': encoder_settings,
                'input_attachments': input_attachments,
                'input_specification': input_specification,
                'log_level': log_level,
                'maintenance': maintenance,
                'role_arn': role_arn,
                'channel_engine_version': channel_engine_version,
                'dry_run': dry_run,
                'anywhere_settings': anywhere_settings,
                'tags': tags,
                'purge_tags': purge_tags,
                'request_id': str(uuid.uuid4())
            }

            manager.do_update_channel(update_params)

        # Case create
        else:
            create_params = {
                'channel_id': channel_id,
                'name': channel_name,
                'cdi_input_specification': cdi_input_specification,
                'channel_class': channel_class,
                'destinations': destinations,
                'encoder_settings': encoder_settings,
                'input_attachments': input_attachments,
                'input_specification': input_specification,
                'log_level': log_level,
                'maintenance': maintenance,
                'reserved': reserved,
                'role_arn': role_arn,
                'vpc': vpc,
                'anywhere_settings': anywhere_settings,
                'channel_engine_version': channel_engine_version,
                'dry_run': dry_run,
                'tags': tags,
                'request_id': str(uuid.uuid4())
            }
            
            manager.do_create_channel(create_params)
            channel_id = manager.channel.get('channel_id')
            
            # Wait for the channel to be created
            if wait and channel_id:
                manager.wait_for('channel_created', channel_id, wait_timeout) # type: ignore
                manager.get_channel_by_id(channel_id)
                
    # Handle absent state
    elif state == 'absent':
        if manager.channel:
            # Channel exists, delete it
            channel_id = manager.channel.get('channel_id')
            manager.delete_channel(channel_id) # type: ignore
            
            # Wait for the channel to be deleted if requested
            if wait and channel_id:
                manager.wait_for('channel_deleted', channel_id, wait_timeout) # type: ignore

    module.exit_json(changed=manager.changed, channel=manager.channel)


if __name__ == '__main__':
    main()
