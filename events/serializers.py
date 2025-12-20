from rest_framework import serializers

from .models import Event, Ticket, TicketPurchase, VirtualMeeting

class VirtualMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualMeeting
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'event']

class TicketSerializer(serializers.ModelSerializer):
    sales_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Ticket
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'quantity_sold', 'sales_price', 'event']

class EventSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, required=False)
    platform = serializers.ChoiceField(choices=VirtualMeeting.Platform, required=False, write_only=True)
    redirect_after_auth = serializers.URLField(required=False, write_only=True)
    
    virtual_meeting = VirtualMeetingSerializer(required=False, read_only=True)
    
    class Meta:
        model = Event
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'google_event_id', 'google_meet_link', 'is_cancelled', 'creator']
        
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        
        mode = validated_data.get("mode")
        platform = validated_data.get("platform")
        
        if (mode == Event.Mode.PHYSICAL or mode == Event.Mode.HYBRID) and not platform:
            raise serializers.ValidationError({"platform": "Platform is required for events with virtual or hybrid modes"})
        
        return validated_data
        
    def create(self, validated_data):
        tickets_data = validated_data.pop('tickets', [])
        # validated_data.
        # mode = validated_data.get('mode')
        
        event = super().create(validated_data)
        
        for ticket_data in tickets_data:
            Ticket.objects.create(event=event, **ticket_data)
        
        return event
        