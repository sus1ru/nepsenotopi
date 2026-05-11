from rest_framework import serializers

from nepse.models import (
    Company,
    InstrumentType,
    Security,
    SecurityLog,
    Sector,
    ShareGroup,
)


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'


class ShareGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareGroup
        fields = '__all__'


class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = '__all__'


class InstrumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentType
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    sector_description = serializers.CharField(
        source='sector.sector_description',
        read_only=True
    )
    instrument_type_code = serializers.CharField(
        source='instrument_type.code',
        read_only=True
    )
    security_symbol = serializers.CharField(
        source='security.symbol',
        read_only=True
    )

    class Meta:
        model = Company
        fields = '__all__'


class SecurityLogSerializer(serializers.ModelSerializer):
    security_symbol = serializers.CharField(source='security.symbol', read_only=True)

    class Meta:
        model = SecurityLog
        fields = '__all__'
