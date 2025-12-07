from rest_framework import serializers

from .models import Event, Ticket, TicketPurchase

class TicketSerializer(serializers.ModelSerializer):
    sales_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Ticket
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'quantity_sold', 'sales_price', 'event']

class EventSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, required=False)
    
    class Meta:
        model = Event
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'google_event_id', 'google_meet_link', 'is_cancelled', 'creator']
        
    def create(self, validated_data):
        tickets_data = validated_data.pop('tickets', [])
        event = super().create(validated_data)
        
        for ticket_data in tickets_data:
            Ticket.objects.create(event=event, **ticket_data)
        
        return event
        