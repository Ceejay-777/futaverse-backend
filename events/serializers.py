from django.utils import timezone

from rest_framework import serializers

from .models import Event, Ticket, TicketPurchase, VirtualMeeting

class VirtualMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualMeeting
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['sqid', 'created_at', 'updated_at', 'event']

class CreateTicketSerializer(serializers.ModelSerializer):
    event = serializers.SlugRelatedField(queryset=Event.objects.all(), slug_field='sqid')
    sales_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Ticket
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['sqid', 'created_at', 'updated_at', 'quantity_sold', 'sales_price']
        
class TicketSerializer(serializers.ModelSerializer):
    sales_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Ticket
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['sqid', 'created_at', 'updated_at', 'quantity_sold', 'sales_price']

class EventSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, required=False)
    platform = serializers.ChoiceField(choices=VirtualMeeting.Platform, required=False, write_only=True)
    redirect_after_auth = serializers.URLField(required=False, write_only=True)
    
    virtual_meeting = VirtualMeetingSerializer(required=False, read_only=True)
    
    class Meta:
        model = Event
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['sqid', 'created_at', 'updated_at', 'google_event_id', 'google_meet_link', 'is_cancelled', 'creator']
        
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        
        mode = validated_data.get("mode")
        platform = validated_data.get("platform")
        
        if (mode == Event.Mode.PHYSICAL or mode == Event.Mode.HYBRID) and not platform:
            raise serializers.ValidationError({"platform": "Platform is required for events with virtual or hybrid modes"})
        
        return validated_data
        
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets", None)
        event = super().create(validated_data)
        
        if not tickets_data:
            Ticket.objects.create(event=event, name="Free", description="Standard", price=0, type=Ticket.Type.DEFAULT)
          
        if tickets_data:    
            for ticket_data in tickets_data:
                Ticket.objects.create(event=event, **ticket_data)
        
        return event
    
class TicketPurchaseSerializer(serializers.ModelSerializer):
    ticket = serializers.SlugRelatedField(queryset=Ticket.objects.all(), slug_field='sqid')
    email = serializers.EmailField(write_only=True, required=False)
    
    class Meta:
        model = TicketPurchase
        fields = ['ticket', 'email']
        read_only_fields = ['sqid', 'created_at', 'updated_at']
        
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        
        ticket: Ticket = validated_data.get('ticket')
        
        if ticket.is_active == False:
            raise serializers.ValidationError({"ticket": "Ticket is not active"})
        
        if ticket.sales_start > timezone.now():
            raise serializers.ValidationError({"ticket": "Ticket sales have not started yet"})
        
        if ticket.sales_end and ticket.sales_end < timezone.now():
            raise serializers.ValidationError({"ticket": "Ticket sales have ended"})
        
        if  ticket.quantity is not None and ticket.quantity_sold >= ticket.quantity:
            raise serializers.ValidationError({"ticket": "Ticket is sold out"})
        
        return validated_data
    
class UpdateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'start_time', 'duration_mins', 'venue', 'max_capacity', 'allow_sponsorship', 'allow_donations', 'is_published', 'is_cancelled']
        read_only_fields = ['sqid']
        